import subprocess
from pathlib import Path
import pytest
from src.infrastructure.ffmpeg_service import FFmpegService


# =========================================================
# 1. Ejecución exitosa y construcción de comandos
# =========================================================

def test_extract_video_segment_success(mocker):
    """Verifica que FFmpeg se invoque con los argumentos y flags correctos."""
    mock_run = mocker.patch("subprocess.run")

    media_in = "videos/sample.mkv"
    media_out = "output/clip.mp4"
    start_time = 12.5
    end_time = 17.0

    resultado = FFmpegService.extract_video_segment(
        media_path=media_in,
        start_time=start_time,
        end_time=end_time,
        output_path=media_out
    )

    # Verifica el retorno
    assert resultado == media_out

    # Verifica los parámetros pasados a subprocess.run
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    comando = args[0]

    comando_esperado = [
        "ffmpeg",
        "-y",
        "-ss", "12.5",
        "-i", media_in,
        "-t", "4.5",  # 17.0 - 12.5
        "-c:v", "libx264",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "128k",
        media_out
    ]

    assert comando == comando_esperado
    assert kwargs["stdout"] == subprocess.DEVNULL
    assert kwargs["stderr"] == subprocess.PIPE
    assert kwargs["check"] is True


@pytest.mark.parametrize(
    "start, end, duracion_esperada",
    [
        (0.0, 5.0, "5.0"),
        (10.25, 15.75, "5.5"),
        (100.0, 101.23, "1.23"),
    ],
)
def test_extract_video_segment_calculo_duracion(mocker, start, end, duracion_esperada):
    """Verifica el cálculo de duración (-t) para diferentes intervalos de tiempo."""
    mock_run = mocker.patch("subprocess.run")

    FFmpegService.extract_video_segment("video.mp4", start, end, "out.mp4")

    comando = mock_run.call_args[0][0]
    indice_t = comando.index("-t")
    duracion_obtenida = round(float(comando[indice_t + 1]), 2)
    assert duracion_obtenida == round(float(duracion_esperada), 2)


def test_extract_video_segment_soporta_objetos_path(mocker):
    """Verifica que acepte objetos Path de pathlib sin lanzar errores."""
    mock_run = mocker.patch("subprocess.run")

    path_in = Path("videos/anime.mkv")
    path_out = Path("output/frase.mp4")

    resultado = FFmpegService.extract_video_segment(path_in, 1.0, 3.0, path_out)

    assert resultado == path_out
    comando = mock_run.call_args[0][0]
    assert str(path_in) in comando
    assert str(path_out) in comando


# =========================================================
# 2. Manejo de errores y excepciones
# =========================================================

def test_extract_video_segment_lanza_runtime_error_con_stderr(mocker):
    """Verifica que capture CalledProcessError y extraiga el mensaje de stderr."""
    error_ffmpeg = b"Error: Invalid data found when processing input"
    mocker.patch(
        "subprocess.run",
        side_effect=subprocess.CalledProcessError(
            returncode=1,
            cmd=["ffmpeg"],
            stderr=error_ffmpeg
        )
    )

    with pytest.raises(RuntimeError) as exc_info:
        FFmpegService.extract_video_segment("in.mp4", 1.0, 2.0, "out.mp4")

    assert "FFmpeg falló al procesar el video" in str(exc_info.value)
    assert "Invalid data found when processing input" in str(exc_info.value)


def test_extract_video_segment_lanza_runtime_error_sin_stderr(mocker):
    """Verifica que maneje el error adecuadamente cuando stderr viene vacío o None."""
    mocker.patch(
        "subprocess.run",
        side_effect=subprocess.CalledProcessError(
            returncode=1,
            cmd=["ffmpeg"],
            stderr=None
        )
    )

    with pytest.raises(RuntimeError) as exc_info:
        FFmpegService.extract_video_segment("in.mp4", 1.0, 2.0, "out.mp4")

    assert "FFmpeg falló al procesar el video" in str(exc_info.value)
