#!/usr/bin/env bash

set -e

DEFAULT_PYTHON_VENV="./wheel_builder_venv"
DEFAULT_BASE_PYTHON="python3"
scriptDir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
DEFAULT_DEV_REQUIREMENTS_FILE="$scriptDir/../requirements-dev.txt"
DEFAULT_OUTPUT_PATH="./dist"

remove_venv(){
    if [ -d $1 ]; then
        echo "removing $1"
        rm -r $1
    fi
}

generate_venv(){
    base_python=$1
    virtual_env=$2
    trap "remove_venv $virtual_env" ERR SIGINT SIGTERM
    $base_python -m venv $virtual_env
    . $virtual_env/bin/activate
    python_version=$(python --version)

    UV_VERSION=$(grep "^uv==" $DEFAULT_DEV_REQUIREMENTS_FILE)
    if [ -z "${UV_VERSION}" ]; then
        pip install $UV_VERSION
    else
        pip install uv
    fi

    PYTHON_BUILD_VERSION=$(grep "^build==" $DEFAULT_DEV_REQUIREMENTS_FILE)
    if [ -z "${PYTHON_BUILD_VERSION}" ]; then
        UV_INDEX_STRATEGY=unsafe-best-match uv pip install $PYTHON_BUILD_VERSION
    else
        pip install build
    fi

    echo "Created a build env based on $python_version"
}

generate_wheel(){
    virtual_env=$1
    PROJECT_ROOT=$2
    OUTPUT_PATH=$3
    TMP_OUTPUT_PATH=$(mktemp -d /tmp/python_wheels.XXXXXX)
    . $virtual_env/bin/activate
    python_version=$(python --version)
    UV_INDEX_STRATEGY=unsafe-best-match python -m build $PROJECT_ROOT --wheel --installer=uv --outdir=$TMP_OUTPUT_PATH
    auditwheel repair $TMP_OUTPUT_PATH/*.whl -w $OUTPUT_PATH
}

print_usage(){
    echo "Usage: $0 project_root [--venv_path optional_path][--force-venv-creation][--base-python[=path_to_python_exec]]"
}

show_help() {
  print_usage
  echo
  echo "Arguments:"
  echo "  project_root          Path to Python project containing pyproject.toml file."
  echo "  --force-venv-creation  Recreate venv even if currently exists"
  echo "  --venv_path[=path]    Path used to install build tools. Defaults to '$DEFAULT_PYTHON_VENV'."
  echo "  --base-python[=path_to_python_exec]  Path used to base Python version. Used for generating the build virtual environment."
  echo "  --help, -h            Display this help message."
}


check_args(){
    if [[ -n "$base_python_path" ]]; then
        python_used_full_path=$(which $base_python_path)
        if [ ! -f "$python_used_full_path" ]; then
          echo "Error: $base_python_path does not exist."
          print_usage
          exit 1
        fi
    fi
    if [[ -f "$project_root" ]]; then
        echo "error: project_root should point to a directory not a file"
        print_usage
        exit 1
    fi
    if [[ ! -f "$project_root/pyproject.toml" ]]; then
        echo "error: $project_root contains no pyproject.toml"
        exit 1
    fi
}

# Check if the help flag is provided
for arg in "$@"; do
    if [[ "$arg" == "--help" || "$arg" == "-h" ]]; then
    show_help
    exit 0
  fi
done

# Check if the project_root argument is provided
if [ -z "$1" ]; then
  print_usage
  exit 1
fi

# Assign the project_root argument to a variable
project_root=$1

# venv_path value is set to default
venv_path=$DEFAULT_PYTHON_VENV

# base_python_path value is set to default
base_python_path=$DEFAULT_BASE_PYTHON
force_rebuild_venv=false

# Parse optional arguments
while [[ "$#" -gt 0 ]]; do
  case $1 in
    --venv-path=*)
      venv_path="${1#*=}"
      shift
      ;;
    --venv-path)
      venv_path="$2"
      shift 2
      ;;
    --base-python=*)
      base_python_path=$(which "${1#*=}")
      shift
      ;;
    --base-python)
      base_python_path=$(which "$2")
      shift 2
      ;;
    --force-venv-creation)
      force_rebuild_venv=true
      shift
      ;;

    *)
      shift
      ;;
  esac
done

# Output the values

check_args
build_virtual_env=$venv_path
if [ ! -f "$build_virtual_env/bin/python" ] || [ "$force_rebuild_venv" == true ]; then
    generate_venv $base_python_path $build_virtual_env
else
    echo "Using existing venv: $build_virtual_env"
fi
generate_wheel $build_virtual_env $project_root $DEFAULT_OUTPUT_PATH
