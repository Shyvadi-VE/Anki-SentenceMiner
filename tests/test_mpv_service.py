import pytest
from unittest.mock import MagicMock
from src.infrastructure.mpv_service import MPVServices


@pytest.fixture
def mock_mpv():
    """Simula la instancia del reproductor MPV sin abrir ventana ni audio."""
    return MagicMock()


@pytest.fixture
def service(mock_mpv):
    """Instancia de MPVServices con el cliente MPV mockeado."""
    srv = MPVServices()
    srv.mpv = mock_mpv
    return srv


# =========================================================
# 1. Ciclo de vida: Inicialización, Start y Stop
# =========================================================

def test_init():
    """Verifica el estado inicial del servicio."""
    nuevo_servicio = MPVServices()
    assert nuevo_servicio.mpv is None
    assert nuevo_servicio.frases_minadas == []


def test_start_inicializa_reproductor(mocker):
    """Verifica que start() instancie MPV con los flags adecuados."""
    mock_mpv_class = mocker.patch("src.infrastructure.mpv_service.MPV")

    nuevo_servicio = MPVServices()
    nuevo_servicio.start()

    mock_mpv_class.assert_called_once_with(start_mpv=True, idle="yes")
    assert nuevo_servicio.mpv is not None


def test_stop_termina_reproductor(service, mock_mpv):
    """Verifica que stop() finalice el proceso MPV."""
    service.stop()
    mock_mpv.terminate.assert_called_once()


def test_stop_con_excepcion_no_falla(service, mock_mpv):
    """Verifica que stop() capture excepciones sin lanzar error al usuario."""
    mock_mpv.terminate.side_effect = RuntimeError("Proceso ya cerrado")
    # No debe levantar ninguna excepción
    service.stop()


def test_stop_cuando_mpv_es_none():
    """Verifica que stop() funcione sin errores si MPV no fue iniciado."""
    srv = MPVServices()
    srv.mpv = None
    srv.stop()


# =========================================================
# 2. Métodos auxiliares y procesamiento de texto
# =========================================================

@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("Hola mundo\n", "Hola mundo"),
        ("\nTexto con\nsaltos múltiples\n", "Texto con saltos múltiples"),
        ("   Espacios al inicio y final   ", "Espacios al inicio y final"),
        ("Línea 1\n Línea 2", "Línea 1  Línea 2"),
    ],
)
def test_limpiar_texto(entrada, esperado):
    """Verifica la eliminación de saltos de línea y espacios sobrantes."""
    assert MPVServices._limpiar_texto(entrada) == "esperado".replace("esperado", esperado)


# =========================================================
# 3. Carga de video y configuración
# =========================================================

def test_cargar_video(service, mock_mpv, mocker):
    """Verifica que se llame a play y se espere el tiempo de buffer."""
    mock_sleep = mocker.patch("time.sleep")
    ruta = "C:/media/video.mp4"

    service._cargar_video(ruta)

    mock_mpv.play.assert_called_once_with(ruta)
    mock_sleep.assert_called_once_with(1.5)


def test_configurar_subtitulos_encuentra_track(service, mock_mpv):
    """Verifica que active el subtítulo al encontrar un track de tipo 'sub'."""
    mock_mpv.track_list = [
        {"type": "video", "id": 1},
        {"type": "audio", "id": 2},
        {"type": "sub", "id": 3},
        {"type": "sub", "id": 4},
    ]

    service._configurar_subtitulos()
    assert mock_mpv.sid == 3


def test_configurar_subtitulos_sin_tracks(service, mock_mpv, mocker):
    """Verifica el aviso en consola cuando no hay tracks de subtítulos."""
    mock_mpv.track_list = [
        {"type": "video", "id": 1},
        {"type": "audio", "id": 2},
    ]
    mock_print = mocker.patch("builtins.print")

    service._configurar_subtitulos()
    mock_print.assert_called_with("AVISO: No se encontraron subtítulos.")


def test_registrar_atajos(service, mock_mpv):
    """Verifica que se enlace la tecla 's' con la acción de guardar."""
    service._registrar_atajos()
    mock_mpv.bind_key_press.assert_called_once_with("s", service._accion_guardar)


# =========================================================
# 4. Acción de minado / guardado (_accion_guardar)
# =========================================================

def test_accion_guardar_agrega_frase_valida(service, mock_mpv, mocker):
    """Verifica que guarde la frase minada con tiempos redondeados y texto limpio."""
    mocker.patch("builtins.print")
    mock_mpv.sub_text = "Good morning everyone!\n"
    mock_mpv.sub_start = 14.2567
    mock_mpv.sub_end = 17.8912

    service._accion_guardar()

    assert len(service.frases_minadas) == 1
    frase = service.frases_minadas[0]
    assert frase["texto"] == "Good morning everyone!"
    assert frase["tiempo_inicio"] == 14.26
    assert frase["tiempo_fin"] == 17.89


@pytest.mark.parametrize(
    "sub_text, sub_start, sub_end",
    [
        (None, 1.0, 2.0),
        ("", 1.0, 2.0),
        ("Texto válido", None, 2.0),
        ("Texto válido", 1.0, None),
    ],
)
def test_accion_guardar_ignora_subtitulos_invalidos(service, mock_mpv, sub_text, sub_start, sub_end):
    """Verifica que ignore llamadas con subtítulos incompletos o vacíos."""
    mock_mpv.sub_text = sub_text
    mock_mpv.sub_start = sub_start
    mock_mpv.sub_end = sub_end

    service._accion_guardar()

    assert len(service.frases_minadas) == 0


# =========================================================
# 5. Detección de reproductor activo y monitoreo
# =========================================================

def test_reproductor_activo_cuando_time_pos_existe(service, mock_mpv):
    """Retorna True si time_pos tiene un valor activo."""
    mock_mpv.time_pos = 10.5
    assert service._reproductor_activo() is True


def test_reproductor_activo_retorna_false_si_cierra(service, mock_mpv, mocker):
    """Retorna False si time_pos es None incluso tras la espera."""
    mock_sleep = mocker.patch("time.sleep")
    mock_mpv.time_pos = None

    assert service._reproductor_activo() is False
    mock_sleep.assert_called_once_with(0.5)


def test_monitorear_reproduccion_sale_cuando_cierra(service, mocker):
    """Verifica que el bucle de monitoreo finalice al detectar el cierre."""
    mock_activo = mocker.patch.object(service, "_reproductor_activo", side_effect=[False])

    service._monitorear_reproduccion()
    mock_activo.assert_called_once()


# =========================================================
# 6. Flujo completo: reproducir_y_capturar
# =========================================================

def test_reproducir_y_capturar_flujo_completo(service, mocker):
    """Verifica que el orquestador llame a todos los pasos en orden."""
    mock_cargar = mocker.patch.object(service, "_cargar_video")
    mock_subtitulos = mocker.patch.object(service, "_configurar_subtitulos")
    mock_atajos = mocker.patch.object(service, "_registrar_atajos")
    mock_monitorear = mocker.patch.object(service, "_monitorear_reproduccion")

    ruta = "C:/media/sample.mkv"
    service.reproducir_y_capturar(ruta)

    mock_cargar.assert_called_once_with(ruta)
    mock_subtitulos.assert_called_once()
    mock_atajos.assert_called_once()
    mock_monitorear.assert_called_once()
