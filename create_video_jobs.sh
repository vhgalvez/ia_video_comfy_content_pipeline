#!/usr/bin/env bash
set -euo pipefail

# =========================================================
# create_video_jobs.sh
#
# Crea / completa la estructura estándar dentro de cada job
# existente del dataset de video.
#
# Comportamiento:
# - Detecta automáticamente los directorios dentro de jobs/
# - Crea la estructura mínima editorial
# - Crea carpetas visuales manuales
# - Permite elegir si preparar vertical, horizontal o ambos
#
# Uso:
#   bash wsl/create_video_jobs.sh
#   bash wsl/create_video_jobs.sh --target vertical
#   bash wsl/create_video_jobs.sh --target horizontal
#   bash wsl/create_video_jobs.sh --target both
#   bash wsl/create_video_jobs.sh --job-id 000001 --target vertical
#
# Variables opcionales:
#   VIDEO_DATASET_ROOT
#   VIDEO_JOBS_ROOT
# =========================================================

DATASET_ROOT="${VIDEO_DATASET_ROOT:-/mnt/c/Users/vhgal/Documents/desarrollo/ia/AI-video-automation/video-dataset}"
JOBS_ROOT="${VIDEO_JOBS_ROOT:-${DATASET_ROOT}/jobs}"

# Opciones válidas:
#   vertical
#   horizontal
#   both
TARGET="vertical"
ONLY_JOB_ID=""

usage() {
  cat <<EOF
Uso:
  bash wsl/create_video_jobs.sh [--target vertical|horizontal|both] [--job-id 000001]

Opciones:
  --target   Define qué estructura de render crear.
             Valores:
               vertical   -> crea timeline/output vertical
               horizontal -> crea timeline/output horizontal
               both       -> crea ambas

  --job-id   Limita la operación a un solo job existente.

Variables soportadas:
  VIDEO_DATASET_ROOT
  VIDEO_JOBS_ROOT

Defaults:
  DATASET_ROOT=${DATASET_ROOT}
  JOBS_ROOT=${JOBS_ROOT}
  TARGET=${TARGET}
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET="${2:-}"
      shift 2
      ;;
    --job-id)
      ONLY_JOB_ID="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Argumento no reconocido: $1"
      usage
      exit 1
      ;;
  esac
done

case "${TARGET}" in
  vertical|horizontal|both)
    ;;
  *)
    echo "Valor inválido para --target: ${TARGET}"
    echo "Usa: vertical | horizontal | both"
    exit 1
    ;;
esac

mkdir -p "${JOBS_ROOT}"

discover_jobs() {
  if [[ -n "${ONLY_JOB_ID}" ]]; then
    if [[ -d "${JOBS_ROOT}/${ONLY_JOB_ID}" ]]; then
      echo "${ONLY_JOB_ID}"
      return 0
    else
      echo "El job ${ONLY_JOB_ID} no existe en ${JOBS_ROOT}" >&2
      return 1
    fi
  fi

  find "${JOBS_ROOT}" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort
}

create_job_structure() {
  local job_id="$1"
  local job_root="${JOBS_ROOT}/${job_id}"

  echo "Procesando job: ${job_id}"

  # -------------------------------------------------------
  # Estructura editorial base
  # -------------------------------------------------------
  mkdir -p \
    "${job_root}/source" \
    "${job_root}/audio" \
    "${job_root}/subtitles" \
    "${job_root}/logs"

  # -------------------------------------------------------
  # Estructura visual manual
  # -------------------------------------------------------
  mkdir -p \
    "${job_root}/images/previews" \
    "${job_root}/videos/previews"

  # -------------------------------------------------------
  # Estructura de render por target
  # -------------------------------------------------------
  case "${TARGET}" in
    vertical)
      mkdir -p \
        "${job_root}/timeline/vertical" \
        "${job_root}/output/vertical"
      ;;
    horizontal)
      mkdir -p \
        "${job_root}/timeline/horizontal" \
        "${job_root}/output/horizontal"
      ;;
    both)
      mkdir -p \
        "${job_root}/timeline/vertical" \
        "${job_root}/timeline/horizontal" \
        "${job_root}/output/vertical" \
        "${job_root}/output/horizontal"
      ;;
  esac

  # -------------------------------------------------------
  # job.json
  # Solo se crea si no existe
  # -------------------------------------------------------
  if [[ ! -f "${job_root}/job.json" ]]; then
    cat > "${job_root}/job.json" <<EOF
{
  "job_id": "${job_id}",
  "job_schema_version": "2.0",
  "created_at": "",
  "updated_at": "",
  "voice": {},
  "render_targets": ["${TARGET}"],
  "paths": {
    "brief": "jobs/${job_id}/source/${job_id}_brief.json",
    "script": "jobs/${job_id}/source/${job_id}_script.json",
    "visual_manifest": "jobs/${job_id}/source/${job_id}_visual_manifest.json",
    "rendered_comfy_workflow": "jobs/${job_id}/source/${job_id}_rendered_comfy_workflow.json",
    "audio": "jobs/${job_id}/audio/${job_id}_narration.wav",
    "subtitles": "jobs/${job_id}/subtitles/${job_id}_narration.srt",
    "logs_dir": "jobs/${job_id}/logs",
    "images_dir": "jobs/${job_id}/images",
    "videos_dir": "jobs/${job_id}/videos"
  }
}
EOF
  fi

  # -------------------------------------------------------
  # status.json
  # Solo se crea si no existe
  # -------------------------------------------------------
  if [[ ! -f "${job_root}/status.json" ]]; then
    cat > "${job_root}/status.json" <<EOF
{
  "brief_created": false,
  "script_generated": false,
  "audio_generated": false,
  "subtitles_generated": false,
  "visual_manifest_generated": false,
  "images_ready": false,
  "videos_ready": false,
  "render_vertical_ready": false,
  "render_horizontal_ready": false,
  "export_ready": false,
  "last_step": "created",
  "updated_at": "",
  "voice_id": "",
  "voice_scope": "",
  "voice_source": "",
  "voice_name": "",
  "voice_selection_mode": "",
  "voice_model_name": "",
  "voice_reference_file": "",
  "audio_file": "",
  "audio_generated_at": ""
}
EOF
  fi

  echo "OK -> ${job_root}"
  echo
}

JOB_LIST="$(discover_jobs || true)"

if [[ -z "${JOB_LIST}" ]]; then
  echo "No se encontraron directorios de jobs en: ${JOBS_ROOT}"
  echo "Primero crea jobs como 000001, 000002, etc."
  exit 1
fi

while IFS= read -r job_id; do
  [[ -z "${job_id}" ]] && continue
  create_job_structure "${job_id}"
done <<< "${JOB_LIST}"

echo "Estructura completada en: ${JOBS_ROOT}"
echo "Target usado: ${TARGET}"