from datetime import datetime
import os
import pandas as pd
import pytz
import streamlit as st

# --- CONFIGURACIÓN DE LA PÁGINA ---
LOGO_FILE = "fulcar_logo.png"

st.set_page_config(
    page_title="Control de Vehículos - Fulcar AUTO",
    page_icon="🚗",
    layout="centered",
)

# --- ESTILOS CSS ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    h1, h3 {
        color: #1a1a1a;
        text-align: center;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- ENCABEZADO CON LOGO ---
col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
  if os.path.exists(LOGO_FILE):
    st.image(LOGO_FILE, use_container_width=True)
  else:
    st.warning(f"⚠️ Falta el archivo '{LOGO_FILE}'")

st.markdown(
    "<h3 style='text-align: center; color: #444; margin-top: -10px;"
    " margin-bottom: 25px; font-size: 1.2rem;'>Control de Vehículos e"
    " Inventario (Supabase Cloud)</h3>",
    unsafe_allow_html=True,
)

# --- CONEXIÓN SQL PERMANENTE CON SUPABASE ---
conn = st.connection("sql", type="sql")


def obtener_tiempo_rd():
  """Obtiene la fecha y hora actual en zona horaria de Santo Domingo (RD)

  en formato DD/MM/YYYY hh:mm a.m./p.m.
  """
  try:
    tz_rd = pytz.timezone("America/Santo_Domingo")
    ahora_rd = datetime.now(tz_rd)
    return (
        ahora_rd.strftime("%d/%m/%Y %I:%M %p")
        .lower()
        .replace("am", "a. m.")
        .replace("pm", "p. m.")
    )
  except Exception:
    return (
        datetime.now()
        .strftime("%d/%m/%Y %I:%M %p")
        .lower()
        .replace("am", "a. m.")
        .replace("pm", "p. m.")
    )


def cargar_datos():
  try:
    df = conn.query("SELECT * FROM clientes_vehiculos;", ttl=0)
    if df is not None and not df.empty:
      return df
  except Exception as e:
    st.info(
        "ℹ️ Conectando con la base de datos en la nube (tabla inicial"
        " vacía)..."
    )

  return pd.DataFrame(
      columns=[
          "id",
          "fecha_hora",
          "registrado_por",
          "cliente",
          "telefono",
          "vehiculo",
          "nota",
      ]
  )


def guardar_registro_en_db(
    nuevo_id, fecha_hora, reg_por, cliente, tel, vehiculo, nota
):
  with conn.session as s:
    s.execute(
        "INSERT INTO clientes_vehiculos (id, fecha_hora, registrado_por,"
        " cliente, telefono, vehiculo, nota) VALUES (:id, :fh, :rp, :cl, :tel,"
        " :veh, :nota)",
        {
            "id": str(nuevo_id),
            "fh": fecha_hora,
            "rp": reg_por,
            "cl": cliente,
            "tel": tel,
            "veh": vehiculo,
            "nota": nota,
        },
    )
    s.commit()


def actualizar_db_completa(df):
  with conn.session as s:
    s.execute("DELETE FROM clientes_vehiculos;")
    for _, row in df.iterrows():
      s.execute(
          "INSERT INTO clientes_vehiculos (id, fecha_hora, registrado_por,"
          " cliente, telefono, vehiculo, nota) VALUES (:id, :fh, :rp, :cl, :tel,"
          " :veh, :nota)",
          {
              "id": str(row["id"]),
              "fh": row["fecha_hora"],
              "rp": row["registrado_por"],
              "cl": row["cliente"],
              "tel": row["telefono"],
              "veh": row["vehiculo"],
              "nota": row["nota"],
          },
      )
    s.commit()


# Cargar datos actuales desde Supabase
df_registros = cargar_datos()

# Mapeo visual de columnas amigables
df_mostrar = (
    df_registros.rename(
        columns={
            "id": "ID",
            "fecha_hora": "Fecha/Hora",
            "registrado_por": "Registrado Por",
            "cliente": "Cliente",
            "telefono": "Teléfono",
            "vehiculo": "Vehículo",
            "nota": "Nota",
        }
    )
    if not df_registros.empty
    else pd.DataFrame(
        columns=[
            "ID",
            "Fecha/Hora",
            "Registrado Por",
            "Cliente",
            "Teléfono",
            "Vehículo",
            "Nota",
        ]
    )
)

# --- INTERFAZ SUPERIOR (Desplegable de Vehículos) ---
with st.expander("🚙 Ver Vehículos Registrados en el Sistema"):
  if not df_mostrar.empty and "Vehículo" in df_mostrar.columns:
    vehiculos_unicos = df_mostrar["Vehículo"].dropna().unique()
    if len(vehiculos_unicos) > 0:
      st.write("Lista de vehículos en inventario:")
      for v in vehiculos_unicos:
        st.markdown(f"- 🚗 **{v}**")
    else:
      st.info("No hay vehículos registrados todavía.")
  else:
    st.info("Base de datos en la nube vacía.")

st.markdown("")

# --- FORMULARIO DE REGISTRO ---
st.markdown("### 📝 Registrar Nuevo Cliente / Vehículo")

with st.form("form_registro", clear_on_submit=True):
  nombre_cliente = st.text_input("👤 Nombre y Apellido del Cliente")
  telefono = st.text_input(
      "📱 Número de Teléfono", placeholder="Ej: 809-000-0000"
  )
  registrado_por = st.text_input(
      "✍️ Registrado por (Tu nombre o usuario)", placeholder="Ej: Frank"
  )

  vehiculos_existentes = (
      list(df_mostrar["Vehículo"].dropna().unique())
      if not df_mostrar.empty and "Vehículo" in df_mostrar.columns
      else []
  )

  if len(vehiculos_existentes) > 0:
    opciones_desplegable = ["-- Escribir nuevo vehículo --"] + (
        vehiculos_existentes
    )
    vehiculo_elegido = st.selectbox(
        "🚘 Seleccione o Escriba el Vehículo", options=opciones_desplegable
    )

    if vehiculo_elegido == "-- Escribir nuevo vehículo --":
      vehiculo = st.text_input(
          "🚗 Especifique el Nuevo Vehículo (Marca, Modelo, Año...)"
      )
    else:
      vehiculo = vehiculo_elegido
  else:
    vehiculo = st.text_input(
        "🚗 Vehículo (Escribe el primero: Marca, Modelo, Año...)"
    )

  nota = st.text_area(
      "📋 Nota u Observaciones",
      placeholder="Detalles de entrada, estado del vehículo, motivo...",
  )

  submitted = st.form_submit_button(
      "💾 Guardar en la Nube", use_container_width=True
  )

  if submitted:
    if not nombre_cliente or not telefono or not vehiculo or not registrado_por:
      st.error(
          "⚠️ Por favor completa los campos obligatorios: Cliente, Teléfono,"
          " Vehículo y Registrado Por."
      )
    else:
      max_id = 0
      if not df_registros.empty and "id" in df_registros.columns:
        try:
          max_id = pd.to_numeric(df_registros["id"], errors="coerce").max()
          if pd.isna(max_id):
            max_id = len(df_registros)
        except:
          max_id = len(df_registros)

      nuevo_id = str(int(max_id) + 1)
      fecha_hora_rd = obtener_tiempo_rd()

      # Guardar directamente en la base de datos de Supabase
      guardar_registro_en_db(
          nuevo_id,
          fecha_hora_rd,
          registrado_por,
          nombre_cliente,
          telefono,
          vehiculo,
          nota,
      )
      st.success(
          f"✅ ¡Vehículo para {nombre_cliente} guardado en la nube con éxito!"
      )
      st.rerun()

st.markdown("---")

# --- VISTA GENERAL DE REGISTROS ---
st.markdown("### 📊 Base de Datos de Registros (En Vivo)")

if not df_mostrar.empty:
  busqueda = st.text_input(
      "🔍 Buscar cliente, teléfono o vehículo:", placeholder="Escribe para filtrar..."
  )
  if busqueda:
    df_filtrado = df_mostrar[
        df_mostrar.astype(str)
        .apply(lambda x: x.str.contains(busqueda, case=False, na=False))
        .any(axis=1)
    ]
  else:
    df_filtrado = df_mostrar

  st.dataframe(
      df_filtrado.drop(columns=["ID"])
      if "ID" in df_filtrado.columns
      else df_filtrado,
      use_container_width=True,
      hide_index=True,
  )

  csv_data = df_mostrar.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="📥 Descargar Respaldo en CSV",
      data=csv_data,
      file_name="respaldo_fulcar.csv",
      mime="text/csv",
      use_container_width=True,
  )
else:
  st.info("ℹ️ La base de datos en la nube está conectada y lista.")

# --- PANEL DE ADMINISTRADOR ---
st.markdown("---")
with st.expander("🔐 Panel de Administrador (Edición / Corrección de Datos)"):
  password_admin = st.text_input(
      "Contraseña de Administrador", type="password"
  )

  if password_admin == "Fulcar0131":
    st.success("✅ Acceso concedido.")

    if not df_mostrar.empty:
      st.warning(
          "⚠️ **INTERFAZ DE EDICIÓN REAL:** Haz doble clic en cualquier celda"
          " de la tabla de abajo para corregir datos directamente."
      )

      df_editado = st.data_editor(
          df_mostrar,
          num_rows="dynamic",
          use_container_width=True,
          key="editor",
          column_config={"ID": st.column_config.Column(disabled=True)},
      )

      if st.button("💾 Guardar Cambios en la Nube"):
        if df_editado["ID"].duplicated().any():
          st.error(
              "Error: Hay IDs duplicados. Por favor, corrige los IDs antes de"
              " guardar."
          )
        else:
          df_para_db = df_editado.rename(
              columns={
                  "ID": "id",
                  "Fecha/Hora": "fecha_hora",
                  "Registrado Por": "registrado_por",
                  "Cliente": "cliente",
                  "Teléfono": "telefono",
                  "Vehículo": "vehiculo",
                  "Nota": "nota",
              }
          )
          actualizar_db_completa(df_para_db)
          st.success("🎉 ¡Supabase actualizado con éxito!")
          st.rerun()

      st.markdown("### 🗑️ Eliminar un registro específico")
      ids_disponibles = list(df_mostrar["ID"].astype(str))
      id_a_borrar = st.selectbox(
          "Selecciona el ID del registro a eliminar permanentemente",
          options=ids_disponibles,
      )

      if st.button(
          "❌ Eliminar Registro Seleccionado (IRREVERSIBLE)", type="primary"
      ):
        df_filtrado_borrado = df_registros[
            df_registros["id"].astype(str) != str(id_a_borrar)
        ]
        actualizar_db_completa(df_filtrado_borrado)
        st.success("🗑️ Registro eliminado de la nube correctamente.")
        st.rerun()
    else:
      st.info("ℹ️ No hay datos para administrar.")
  elif password_admin != "":
    st.error("❌ Contraseña incorrecta.")
