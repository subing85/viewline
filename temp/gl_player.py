from collections import deque

from PySide6 import QtCore

from viewline.playback.cache import FrameCache


class BasePlayer(QtCore.QObject):
    """Base class for media playback.

    This class defines the common playback signals shared by both movie and image sequence players. Concrete player implementations
    should inherit from this class and emit these signals during playback.

    Signals:
        frame_ready (numpy.ndarray):
            Emitted whenever a decoded frame is ready for display.

        frame_changed (int):
            Emitted when the current timeline frame changes.

        cache_changed (list):
            Emitted when cached frames are updated.

        timeline_actived (bool):
            Emitted when playback starts or stops.
    """

    # Image ready for display.
    frame_ready = QtCore.Signal(object)

    # Current timeline frame changed.
    frame_changed = QtCore.Signal(int)

    # Cached frame list updated.
    cache_changed = QtCore.Signal(list)

    # Playback state changed.
    timeline_actived = QtCore.Signal(int)


class MoviePlayer(BasePlayer):
    """Movie playback engine."""

    def __init__(self):
        """Initialize movie player."""

        super().__init__()

        #
        # Decoder
        #

        self.reader = None

        #
        # Audio
        #

        self.audio_player = AudioPlayer()

        #
        # Playback queues
        #

        self.video_queue = deque()

        self.audio_queue = deque()

        #
        # Playback cache
        #

        self.cache = FrameCache(
            max_size=constants.VL_FRAME_CACHE_MAX_SIZE,
        )

        #
        # Playback timer
        #

        self.timer = QtCore.QTimer()

        self.timer.timeout.connect(
            self.update_playback,
        )

        #
        # Playback clock
        #

        self.elapsed_timer = QtCore.QElapsedTimer()

        self.playback_offset = 0.0

        #
        # Playback state
        #

        self.is_playing = False

        self.loop_enabled = False

        #
        # Timeline
        #

        self.start_frame = constants.VL_START_FRAME

        self.frame_count = 0

        #
        # Active AOV
        #

        self.current_aov = "rgb"

        #
        # OpenGL
        #

        self.gl_texture = None

        #
        # OCIO
        #

        self.ocio_shader = None

        self.input_space = None

        self.display = None

        self.view = None

    # ---------------------------------------------------------
    # Reset
    # ---------------------------------------------------------

    def reset(self):
        """Reset the current playback session.

        Responsibilities:
            * Stop playback.
            * Release the active movie reader.
            * Stop audio playback.
            * Clear decoded frame queues.
            * Clear playback cache.
            * Reset playback clock.
            * Reset timeline state.

        Notes:
            This method does not create a new reader. It only
            destroys the current playback session.
        """

        #
        # Stop playback if currently running.
        #

        self.pause()

        #
        # Close the active movie reader.
        #

        if self.reader:

            self.reader.close()

            self.reader = None

        #
        # Shutdown audio playback.
        #

        self.audio_player.close()

        #
        # Remove queued decoded frames.
        #

        self.video_queue.clear()

        self.audio_queue.clear()

        #
        # Clear playback cache.
        #

        self.cache.clear()

        #
        # Reset playback timer.
        #

        self.playback_offset = 0.0

        #
        # Reset playback state.
        #

        self.is_playing = False

        #
        # Reset timeline.
        #

        self.frame_count = 0

        #
        # Notify UI.
        #

        self.cache_changed.emit([])

        self.timeline_actived.emit(False)

    # ---------------------------------------------------------
    # Load
    # ---------------------------------------------------------

    def load(
        self,
        path,
    ):
        """Load a movie file.

        Args:
            path (str):
                Movie filename.

        Workflow:
            1. Destroy previous playback session.
            2. Create MovieReader.
            3. Initialize audio output.
            4. Read movie metadata.
            5. Seek to first frame.
            6. Pre-buffer packets.

        Notes:
            Loading a movie does not automatically begin playback.
        """

        #
        # Destroy previous movie.
        #

        self.reset()

        #
        # Create movie reader.
        #

        self.reader = MovieReader(path)

        #
        # Store frame count.
        #

        self.frame_count = self.reader.frame_count()

        #
        # Initialize audio output.
        #

        if self.reader.has_audio():

            self.audio_player.initialize(
                self.reader.sample_rate(),
                self.reader.channels(),
            )

        #
        # Display first frame.
        #

        self.seek(
            self.start_frame,
        )

        #
        # Fill playback queues.
        #

        self.fill_movie_queue()

        #
        # Update UI.
        #

        self.cache_changed.emit(
            self.cache.cached_frames(),
        )

    # ---------------------------------------------------------
    # Close
    # ---------------------------------------------------------

    def close(self):
        """Shutdown movie player.

        Responsibilities:
            * Stop playback.
            * Destroy decoder.
            * Shutdown audio.
            * Clear queues.
            * Release caches.

        Notes:
            This is normally called when the Review Player closes.
        """

        #
        # Destroy playback session.
        #

        self.reset()

        #
        # Release GPU resources.
        #

        if self.gl_texture:

            self.gl_texture.destroy()

            self.gl_texture = None

        #
        # Release OCIO shader.
        #

        if self.ocio_shader:

            self.ocio_shader.destroy()

            self.ocio_shader = None


class AudioPlayer(QtCore.QObject):
    """Audio playback device.

    Responsible for playback of decoded PCM audio using the Qt Multimedia framework.

    Responsibilities:
        * Initialize the audio output device.
        * Start, pause and stop playback.
        * Accept decoded audio frames.
        * Submit PCM samples to the output device.
        * Flush buffered audio after seeking.
        * Control playback volume.
        * Release audio resources.

    Notes:
        Audio frames supplied by MovieReader are converted into 16-bit PCM samples before being written to the Qt audio device.
    """

    def __init__(self):
        """Initialize the audio player.

        Creates the audio playback controller. The actual audio device is created later by :meth:`initialize`.

        Notes:
            The playback device remains uninitialized until a movie with an audio stream is loaded.
        """

        super().__init__()

        # Qt audio playback device.
        self.audio_sink = None

        # Writable PCM output stream.
        self.io_device = None

        # Audio format information.
        self.sample_rate = 0
        self.channels = 0

        # Playback volume (0.0 - 1.0).
        self.volume = 1.0

    def initialize(self, sample_rate, channels):
        """Initialize the audio output device.

        Creates a Qt audio playback device using the specified sample rate and channel configuration.

        Args:
            sample_rate (int):
                Audio sample rate.

            channels (int):
                Number of playback channels.

        Notes:
            Existing audio devices are automatically released before creating a new one.
        """

        # Release the previous audio device.
        self.close()

        # Store audio format information.
        self.sample_rate = sample_rate
        self.channels = channels

        # Configure the playback format.
        fmt = QtMultimedia.QAudioFormat()
        fmt.setSampleRate(sample_rate)
        fmt.setChannelCount(channels)
        fmt.setSampleFormat(QtMultimedia.QAudioFormat.Int16)

        # Create the Qt audio playback device.
        self.audio_sink = QtMultimedia.QAudioSink(fmt)

        # Increase the playback buffer size for smoother playback.
        self.audio_sink.setBufferSize(65536)

        # Restore the current playback volume.
        self.audio_sink.setVolume(self.volume)

        # Playback stream will be created on first play().
        self.io_device = None

    def play(self):
        """Start or resume audio playback.

        Playback flow:
            1. Ignore playback when no audio device exists.
            2. Create the output stream if playback has not started.
            3. Otherwise resume playback.

        Notes:
            The first playback call creates the writable output stream. Subsequent calls simply resume playback.
        """

        # Ignore playback when audio is unavailable.
        if self.audio_sink is None:
            return

        # Create the output stream on first playback.
        if self.io_device is None:
            self.io_device = self.audio_sink.start()

        # Resume playback.
        else:
            self.audio_sink.resume()

    def pause(self):
        """Pause audio playback.

        Temporarily suspends playback while preserving queued audio samples.

        Notes:
            Playback can later resume from the same position by calling :meth:`play`.
        """

        # Suspend playback.
        if self.audio_sink:
            self.audio_sink.suspend()

    def stop(self):
        """Stop audio playback.

        Stops playback and destroys the active output stream.

        Notes:
            Unlike :meth:`pause`, playback resumes from the beginning after calling :meth:`play`.
        """

        # Stop playback.
        if self.audio_sink:
            self.audio_sink.stop()

            # Output stream becomes invalid.
            self.io_device = None

    def can_accept_frame(self, frame):
        """Return whether the playback device can accept another frame.

        Args:
            frame (av.AudioFrame):
                Decoded audio frame.

        Returns:
            bool:
                True when sufficient playback buffer space exists.
        """

        # Audio device unavailable.
        if self.audio_sink is None:
            return False

        # Playback has not started.
        if self.io_device is None:
            return False

        # Calculate the required PCM buffer size.
        required = frame.samples * self.channels * 2

        # Compare against the available playback buffer.
        return self.audio_sink.bytesFree() >= required

    def write(self, frame):
        """Write a decoded audio frame.

        Converts decoded audio into signed 16-bit PCM samples before submitting them to the Qt audio output device.

        Args:
            frame (av.AudioFrame):
                Decoded audio frame.
        """

        # Ignore invalid frames.
        if frame is None:
            return

        # Playback stream unavailable.
        if self.io_device is None:
            return

        # Convert decoded audio into a NumPy array.
        pcm = frame.to_ndarray()

        # Convert floating-point samples into signed 16-bit PCM.
        if pcm.dtype == numpy.float32:
            pcm = (numpy.clip(pcm, -1.0, 1.0) * 32767.0).astype(numpy.int16)

        # Interleave multi-channel audio.
        if pcm.ndim == 2:
            pcm = pcm.T.reshape(-1)

        # Submit samples to the playback device.
        self.io_device.write(pcm.tobytes())

    def set_volume(self, volume):
        """Set playback volume.

        Args:
            volume (float):
                Playback volume between 0.0 and 1.0.

        Notes:
            Volume changes are applied immediately without interrupting playback.
        """

        # Clamp the requested volume.
        self.volume = max(0.0, min(volume, 1.0))

        # Apply the new volume.
        if self.audio_sink:
            self.audio_sink.setVolume(self.volume)

    def close(self):
        """Release audio resources.

        Stops playback and destroys the current Qt audio device.

        Notes:
            Called automatically when loading a new movie or shutting down the player.
        """

        # Destroy the playback device.
        if self.audio_sink:
            self.audio_sink.stop()
            self.audio_sink.deleteLater()

        # Reset playback resources.
        self.audio_sink = None
        self.io_device = None

    def flush(self):
        """Flush buffered audio samples.

        Clears all queued audio samples from the playback device.

        Notes:
            This method is typically called after seeking to prevent playback of samples belonging to the previous timeline position.
        """

        # Ignore when audio is unavailable.
        if self.audio_sink is None:
            return

        # Clear buffered samples.
        self.audio_sink.reset()

        # Create a fresh writable stream.
        self.io_device = self.audio_sink.start()
