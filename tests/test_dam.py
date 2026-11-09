import pytest

from dam import datos as d
from dam import ingesta as i
from dam import parser as p
from dam.nomenclatura import CAMPOS, CODIGOS, HEREDADOS


def cat() -> i.Catalogo:
    return i.Catalogo(modelos={"ORION", "LUNA"}, variantes={"71010": "ORION", "71020": "ORION"},
                      temas={"SOLAR", "LUNA"})


def plan_de(*archivos: str):
    return i.planificar(list(archivos), cat()).set_index("archivo")


# --- La nomenclatura es coherente consigo misma ---

def test_todo_campo_corresponde_a_un_codigo():
    for campos in CAMPOS.values():
        assert set(campos) <= set(CODIGOS)


def test_las_variantes_no_llevan_video():
    assert all(CODIGOS[c][0] == "imagen" for c in CAMPOS["variante"])


def test_los_heredados_son_imagenes():
    assert all(CODIGOS[c][0] == "imagen" for c, _ in HEREDADOS.values())


# --- Leer un nombre ---

def test_lee_las_tres_partes():
    a = p.leer("ORION_VSET_01.mp4")
    assert a == p.Activo("ORION_VSET_01.mp4", "ORION", "VSET", "01", "vídeo", heredado=False)


def test_identificador_con_guion_bajo():
    assert p.leer("LINEA_2_KV_03.jpg").identificador == "LINEA_2"


def test_codigo_y_extension_en_minusculas():
    a = p.leer("orion_kv_01.JPG")
    assert (a.codigo, a.medio) == ("KV", "imagen")


@pytest.mark.parametrize("codigo", sorted(CODIGOS))
def test_todos_los_codigos_se_leen(codigo):
    ext = ".mp4" if CODIGOS[codigo][0] == "vídeo" else ".jpg"
    assert isinstance(p.leer(f"ORION_{codigo}_01{ext}"), p.Activo)


@pytest.mark.parametrize("sufijo", sorted(HEREDADOS))
def test_heredado_se_traduce(sufijo):
    a = p.leer(f"71010_{sufijo}.jpg")
    assert (a.codigo, a.serie, a.heredado) == (*HEREDADOS[sufijo], True)


@pytest.mark.parametrize("archivo, motivo", [
    ("71010_PK_1.jpg", p.SERIE),
    ("ORION_KV_001.jpg", p.SERIE),
    ("ORION_PKS_01.jpg", p.CODIGO),
    ("ORION-KV-01.jpg", p.FORMULA),
    ("foto final.jpg", p.FORMULA),
    ("_PK_01.jpg", p.FORMULA),
    ("71010_Z.jpg", p.FORMULA),
    ("ORION_KV_01.gif", p.EXTENSION),
    ("ORION_KV_01", p.EXTENSION),
    ("ORION_KV_01.psd", p.EDITABLE),
    ("ficha.pdf", p.EDITABLE),
    ("ORION_VSET_01.jpg", p.MEDIO),
    ("ORION_PK_01.mp4", p.MEDIO),
    ("ORION_A.mp4", p.HEREDADO_VIDEO),
])
def test_rechazo_con_motivo(archivo, motivo):
    assert p.leer(archivo) == p.Rechazo(archivo, motivo)


# --- Del nombre a la ficha y el campo ---

def test_catalogo_dice_donde_vive_cada_identificador():
    c = cat()
    assert c.tablas("ORION") == ["modelo"]
    assert c.tablas("71010") == ["variante"]
    assert c.tablas("solar") == ["tema"]
    assert c.tablas("LUNA") == ["modelo", "tema"]


def test_cada_archivo_a_su_tabla_y_campo():
    plan = plan_de("71010_3PK_01.jpg", "ORION_VMK_01.mp4", "SOLAR_LF_02.jpg")
    assert plan.loc["71010_3PK_01.jpg", ["tabla", "campo"]].tolist() == ["variante", "img_3pk"]
    assert plan.loc["ORION_VMK_01.mp4", ["tabla", "campo"]].tolist() == ["modelo", "vid_mk"]
    assert plan.loc["SOLAR_LF_02.jpg", ["tabla", "campo"]].tolist() == ["tema", "img_lf"]
    assert (plan["estado"] == "cargar").all()


def test_lo_que_la_variante_no_tiene_sube_a_su_modelo():
    f = plan_de("71020_VSET_01.mp4").iloc[0]
    assert (f["estado"], f["tabla"], f["registro"], f["campo"], f["nota"]) == (
        "cargar", "modelo", "ORION", "vid_set", i.AL_MODELO)


def test_registro_en_mayusculas():
    assert plan_de("orion_KV_01.jpg").iloc[0]["registro"] == "ORION"


@pytest.mark.parametrize("archivo, motivo", [
    ("SOLAR_PK_01.jpg", i.SIN_CAMPO),
    ("ORION_2PK_01.jpg", i.SIN_CAMPO),
    ("ORIONN_PK_01.jpg", i.NO_EXISTE),
    ("LUNA_KV_01.jpg", i.DOS_TABLAS),
])
def test_rechazos_del_catalogo(archivo, motivo):
    f = plan_de(archivo).iloc[0]
    assert (f["estado"], f["motivo"]) == ("rechazado", motivo)


def test_el_nombre_nuevo_gana_al_heredado():
    plan = plan_de("71010_A.jpg", "71010_PK_01.png")
    assert plan.loc["71010_A.jpg", "motivo"] == i.SUSTITUIDO
    assert plan.loc["71010_PK_01.png", "estado"] == "cargar"


@pytest.mark.parametrize("archivos", [
    ("ORION_KV_01.jpg", "ORION_KV_01.png"),
    ("71010_A.jpg", "71010_A.png"),
])
def test_dos_iguales_se_rechazan_los_dos(archivos):
    plan = plan_de(*archivos)
    assert (plan["motivo"] == i.CHOQUE).all()


def test_series_distintas_no_chocan():
    assert (plan_de("ORION_KV_01.jpg", "ORION_KV_02.jpg")["estado"] == "cargar").all()


def test_aplicar_simula_por_defecto():
    plan = i.planificar(["ORION_KV_02.jpg", "ORION_KV_01.jpg", "foto.jpg"], cat())
    pim = i.PIMSimulado()
    assert i.aplicar(plan, pim) == 2
    assert pim.fichas == {}
    i.aplicar(plan, pim, simular=False)
    assert list(pim.fichas[("modelo", "ORION", "img_kv")]) == ["01", "02"]


# --- La entrega sintética ---

def test_la_entrega_sintetica_sale_como_se_espera():
    e = d.entrega()
    plan = i.planificar(e["archivo"].tolist(), d.catalogo()).set_index("archivo")
    for archivo, esperado in e.itertuples(index=False):
        f = plan.loc[archivo]
        if esperado in ("cargar", i.AL_MODELO):
            assert f["estado"] == "cargar", archivo
            assert f["nota"] == (i.AL_MODELO if esperado == i.AL_MODELO else None), archivo
        else:
            assert (f["estado"], f["motivo"]) == ("rechazado", esperado), archivo


def test_la_entrega_es_reproducible_y_sin_nombres_repetidos():
    e = d.entrega()
    assert e.equals(d.entrega())
    assert e["archivo"].is_unique


def test_todo_motivo_tiene_etiqueta_en_los_dos_idiomas():
    from dam import graficos as g

    motivos = {getattr(p, m) for m in ("EDITABLE", "EXTENSION", "FORMULA", "CODIGO", "SERIE",
                                       "MEDIO", "HEREDADO_VIDEO")}
    motivos |= {i.NO_EXISTE, i.DOS_TABLAS, i.SIN_CAMPO, i.SUSTITUIDO, i.CHOQUE}
    for idioma in ("es", "en"):
        assert set(g.TEXTOS[idioma]["motivos"]) == motivos
