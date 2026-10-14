"""Ejecución de cortes de audio y snapshots."""
import subprocess
from pathlib import Path

class FFmpegService:
    """Adaptador de infraestructura para procesar audios y videos con FFmpeg."""

    @staticmethod
    def extract_video_segment(
        media_path: str, 
        start_time: float, 
        end_time: float, 
        output_path: str
    ) -> Path:
        """
        Recorta un segmento de video y audio con FFmpeg para tarjetas multimedia de Anki.
        """
        duration = end_time - start_time

        command = [
            "ffmpeg",
            "-y",
            "-ss", str(start_time),   # Búsqueda rápida de inicio
            "-i", str(media_path),    # Archivo de video original
            "-t", str(duration),      # Duración exacta del clip
            "-c:v", "libx264",        # Códec de video compatible con Anki
            "-crf", "22",             # Optimización de calidad/peso
            "-c:a", "aac",            # Códec de audio compatible con MP4
            "-b:a", "128k",           # Calidad de audio estándar
            str(output_path)
        ]

        try:
            subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                check=True
            )
            
            return output_path
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode("utf-8", errors="ignore") if e.stderr else str(e)
            raise RuntimeError(f"FFmpeg falló al procesar el video: {error_msg}")
