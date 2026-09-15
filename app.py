import os
import pandas as pd
import streamlit as st

# --- CONFIGURACIÓN DE LA PÁGINA ---
LOGO_FILE = "fulcar_logo.png"

st.set_page_config(
    page_title="Control de Vehículos - Fulcar AUTO",
    page_icon="🚗",
    layout="centered",
)

# --- ESTILOS CSS PARA HACER TRANSPARENTE EL FONDO BLANCO DE TU LOGO ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* MAGIA CSS: Vuelve transparente el fondo blanco de tu imagen original manteniendo el logo intacto */
    [data-testid="stImage"] img {
        background-color: transparent !important;
        mix-blend-mode: multiply !important;
        filter: contrast(120%);
        display: block;
        margin-left: auto;
        margin-right: auto;
    }

    h1, h3 {
        color: #1a1a1a;
        text-align: center;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- ENCABEZADO CON TU LOGO ORIGINAL ---
col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
  if os.path.exists(LOGO_FILE):
    st.image(LOGO_FILE, use_container_width=True)
  else:
    st.warning(f"⚠️ Falta el archivo '{LOGO_FILE}'")

st.markdown(
    "<h3 style='text-align: center; color: #444; margin-top: -10px;"
    " margin-bottom: 25px; font-size: 1.2rem;'>Control de Vehículos e"
    " Inventario</h3>",
    unsafe_allow_html=True,
)

DB_FILE = "clientes_vehiculos.xlsx"


def cargar_datos():
  if os.path.exists(DB_FILE):
    try:
      return pd.read_excel(DB_FILE)
    except Exception:
      pass
  return pd.DataFrame(
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


def guardar_datos(df):
  df.to_excel(DB_FILE, index=False)


df_registros = cargar_datos()

# Asegurar columna ID única para edición
if not df_registros.empty and "ID" not in df_registros.columns:
  df_registros.insert(0, "ID", [str(i) for i in range(1, len(df_registros) + 1)])
elif not df_registros.empty:
  df_registros["ID"] = df_registros["ID"].astype(str)
elif df_registros.empty:
  df_registros = pd.DataFrame(
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


# --- INTERFAZ SUPERIOR (Desplegable de Vehículos) ---
with st.expander("🚙 Ver Vehículos Registrados en el Sistema"):
  if not df_registros.empty and "Vehículo" in df_registros.columns:
    vehiculos_unicos = df_registros["Vehículo"].dropna().unique()
    if len(vehiculos_unicos) > 0:
      st.write("Lista de vehículos en inventario:")
      for v in vehiculos_unicos:
        st.markdown(f"- 🚗 **{v}**")
    else:
      st.info("No hay vehículos registrados.")
  else:
    st.info("Base de datos vacía.")

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
      list(df_registros["Vehículo"].dropna().unique())
      if not df_registros.empty and "Vehículo" in df_registros.columns
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
      "💾 Guardar Registro", use_container_width=True
  )

  if submitted:
    if not nombre_cliente or not telefono or not vehiculo or not registrado_por:
      st.error(
          "⚠️ Por favor completa los campos obligatorios: Cliente, Teléfono,"
          " Vehículo y Registrado Por."
      )
    else:
      max_id = 0
      if not df_registros.empty and "ID" in df_registros.columns:
        try:
          max_id = df_registros["ID"].astype(int).max()
        except:
          max_id = len(df_registros)

      nuevo_id = str(max_id + 1)

      nuevo_registro = pd.DataFrame(
          [{
              "ID": nuevo_id,
              "Fecha/Hora": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
              "Registrado Por": registrado_por,
              "Cliente": nombre_cliente,
              "Teléfono": telefono,
              "Vehículo": vehiculo,
              "Nota": nota,
          }]
      )
      df_registros = pd.concat(
          [df_registros, nuevo_registro], ignore_index=True
      )
      guardar_datos(df_registros)
      st.success(f"✅ ¡Vehículo para {nombre_cliente} guardado correctamente!")
      st.rerun()

st.markdown("---")

# --- VISTA GENERAL DE REGISTROS ---
st.markdown("### 📊 Base de Datos de Registros")

if not df_registros.empty:
  busqueda = st.text_input(
      "🔍 Buscar cliente, teléfono o vehículo:", placeholder="Escribe para filtrar..."
  )
  if busqueda:
    df_filtrado = df_registros[
        df_registros.astype(str)
        .apply(lambda x: x.str.contains(busqueda, case=False, na=False))
        .any(axis=1)
    ]
  else:
    df_filtrado = df_registros

  st.dataframe(
      df_filtrado.drop(columns=["ID"])
      if "ID" in df_filtrado.columns
      else df_filtrado,
      use_container_width=True,
      hide_index=True,
  )

  with open(DB_FILE, "rb") as f:
    st.download_button(
        label="📥 Descargar Base de Datos en Excel (.xlsx)",
        data=f,
        file_name="base_datos_fulcar.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        use_container_width=True,
    )
else:
  st.info("ℹ️ Aún no hay registros en la base de datos.")

# --- PANEL DE ADMINISTRADOR ---
st.markdown("---")
with st.expander("🔐 Panel de Administrador (Edición / Corrección de Datos)"):
  password_admin = st.text_input(
      "Contraseña de Administrador", type="password"
  )

  if password_admin == "Fulcar0131":
    st.success("✅ Acceso concedido.")

    if not df_registros.empty:
      st.warning(
          "⚠️ **INTERFAZ DE EDICIÓN REAL:** Haz doble clic en cualquier celda"
          " de la tabla de abajo para corregir datos directamente."
      )

      df_editado = st.data_editor(
          df_registros,
          num_rows="dynamic",
          use_container_width=True,
          key="editor",
          column_config={"ID": st.column_config.Column(disabled=True)},
      )

      if st.button("💾 Guardar Cambios y Actualizar Base de Datos"):
        if df_editado["ID"].duplicated().any():
          st.error(
              "Error: Hay IDs duplicados. Por favor, corrige los IDs antes de"
              " guardar."
          )
        else:
          guardar_datos(df_editado)
          st.success("🎉 ¡Base de datos actualizada con éxito!")
          st.rerun()

      st.markdown("### 🗑️ Eliminar un registro específico")
      ids_disponibles = list(df_registros["ID"].astype(str))
      id_a_borrar = st.selectbox(
          "Selecciona el ID del registro a eliminar permanentemente",
          options=ids_disponibles,
      )

      if st.button(
          "❌ Eliminar Registro Seleccionado (IRREVERSIBLE)", type="primary"
      ):
        df_registros = df_registros[
            df_registros["ID"].astype(str) != str(id_a_borrar)
        ]
        if not df_registros.empty:
          df_registros.reset_index(drop=True, inplace=True)
          df_registros.insert(
              0,
              "ID",
              [str(i) for i in range(1, len(df_registros) + 1)],
          )

        guardar_datos(df_registros)
        st.success("🗑️ Registro eliminado correctamente.")
        st.rerun()
    else:
      st.info("ℹ️ No hay datos para administrar.")
  elif password_admin != "":
    st.error("❌ Contraseña incorrecta.")
