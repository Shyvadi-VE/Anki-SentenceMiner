import time
from python_mpv_jsonipc import MPV

class MPVServices:
    def __init__(self):
        self.mpv = None
        self.frases_minadas = []

    def start(self):
        """
        Arranca el motor MPV.
        Guardarlo en la propiedad mpv
        """
        # Iniciamos el reproductor en modo normal (visible y con audio)
        self.mpv = MPV(start_mpv=True, idle="yes")

    def reproducir_y_capturar(self, ruta_video: str):
        """
        Coordina el flujo de reproducción del video, configuración de subtítulos,
        registro de atajos de teclado y el monitoreo de pantalla (teleprompter).
        """
        self._cargar_video(ruta_video)
        self._configurar_subtitulos()
        self._registrar_atajos()
        self._monitorear_reproduccion()

    def _cargar_video(self, ruta_video: str):
        """Inicia la reproducción del video y espera su carga en memoria."""
        self.mpv.play(ruta_video)
        time.sleep(1.5)

    def _configurar_subtitulos(self):

        """Detecta el primer track de subtítulos disponible y lo activa."""

        sub_id = None

        # Buscamos el subtítulo en ingles y lo activamos
        for track in self.mpv.track_list:
            if track.get("type") == "sub":
                sub_id = track.get("id")
                break

        if sub_id:
            self.mpv.sid = sub_id
        else:
            print("AVISO: No se encontraron subtítulos.")

    def _registrar_atajos(self):
        """Asocia las teclas del reproductor a sus acciones correspondientes."""
        self.mpv.bind_key_press("s", self._accion_guardar)

    def _accion_guardar(self):

        """Callback ejecutado al presionar la tecla para minar la frase actual."""

        # Obtenemos el texto
        texto = self.mpv.sub_text
        
        # Obtenemos los límites exactos del subtítulo en pantalla
        inicio = self.mpv.sub_start  
        fin = self.mpv.sub_end       

        # Asegurarnos de que el texto exista y los tiempos no sean nulos
        if texto and inicio is not None and fin is not None:
                # Limpiamos el texto
                texto_limpio = self._limpiar_texto(texto)
                
                # Redondeamos los tiempos a 2 decimales para que se vean limpios
                inicio_fmt = round(inicio, 2)
                fin_fmt = round(fin, 2)

                # Agregamos la frase a la lista
                self.frases_minadas.append({
                    "tiempo_inicio": inicio_fmt,
                    "tiempo_fin": fin_fmt,
                    "texto": texto_limpio
                })

                print(f"¡GUARDADO PARA ANKI! [{inicio_fmt}s -> {fin_fmt}s]: {texto_limpio}")

    @staticmethod
    def _limpiar_texto(texto: str) -> str:

        """Limpia saltos de línea y espacios en blanco de los subtítulos."""
        return texto.replace("\n", " ").strip()

    def _reproductor_activo(self) -> bool:

        """Comprueba si el reproductor sigue activo o si la ventana fue cerrada."""
        
        # Esperamos 0.5 segundos y comprobamos si el reproductor sigue activo
        if self.mpv.time_pos is None:

            time.sleep(0.5)
            if self.mpv.time_pos is None:
                return False
        
        return True

    def _monitorear_reproduccion(self):

        """Bucle principal (polling) que imprime subtítulos en tiempo real como un teleprompter."""
        texto_anterior = None
        
        try:
            while True:
                if not self._reproductor_activo():
                    break

                time.sleep(0.1)

        except Exception as e:
            # Quitamos el 'pass' silencioso para saber si algo falla
            print(f"\nMonitoreo detenido: {e}")

    def stop(self):
        """
        Apaga el motor MPV
        Cierra la ventana del reproductor y termina el Socket IPC de MPV
        """
        if self.mpv:
            try:
                self.mpv.terminate()
            except:
                pass
