#!/usr/bin/env bash

CONTAINER_WORKSPACE=/tmp/workspace

SKIP_DIRS_NAMED=(\
    '.venv' \
    'venv' \
    '.tox' \
    '.git' \
    '.idea' \
    'reports' \
    '.mypy_cache' \
    '__pycache__' \
    'wheelhouse' \
    '.pytest_cache' \
    'uiucprescon.imagevalidate.egg-info'\
    'build' \
)

REMOVE_FILES_FIRST=( \
  'CMakeUserPresets.json' \
  'CMakePresets.json' \
  'conan_toolchain.cmake' \
  'CTestTestfile.cmake' \
  'conandeps_legacy.cmake'
  )


project_source="$1"
output_path="$2"
python_versions_to_use=("${@:3}")
make_shadow_copy() {
    local project_root=$1
    local destination=$2
    echo 'Making a shadow copy to prevent modifying local files'
    prune_expr=()
    for name in "${SKIP_DIRS_NAMED[@]}"; do
        prune_expr+=(-name "$name" -type d -prune -o);
    done

    mkdir -p "${destination}"
    (
        cd "$project_root"
        find . "${prune_expr[@]}" -type d -print | while read -r dir; do
            mkdir -p "${destination}/$dir"
        done
        find . "${prune_expr[@]}" \( -type f -o -type l \) -print | while read -r file; do
            echo "$file"
            ln -sf "${project_root}/$file" "${destination}/$file"
        done
    )
}

cleanup_workspace(){
    local workspace="$1"
    for f in "${REMOVE_FILES_FIRST[@]}"; do
        OFFENDING_FILE="${workspace}/$f"
        if [ -f "$OFFENDING_FILE" ]; then
          echo "Removing copy from temporary working path to avoid issues: $OFFENDING_FILE";
          rm "$OFFENDING_FILE"
        fi;
    done
    echo 'Removing Python cache files'
    find "${workspace}" -type d -name '__pycache__' -exec rm -rf {} +
    find "${workspace}" -type f -name '*.pyc' -exec rm -f {} +

}
create_wheel(){
    local workspace="$1"
    local python_versions_to_use="$2"
    local output_path="$3"
    uv --version
    trap 'set +x' RETURN
    set -x
    uv build --python=$python_versions_to_use --no-managed-python --wheel --out-dir="${output_path}" "${workspace}"
    if [ $? -ne 0 ]; then
      echo "Failed to build wheel for Python $i"
      uv python list --only-installed
      exit 1;
    fi

}

fixup_wheel(){
    local wheel_path="$1"
    local output_path="$2"
    local staging_path=$(mktemp -d -t fixed-staging-XXXXXX)

    echo 'Fixing up wheels'
    auditwheel -v repair "$wheel_path"/*.whl -w $staging_path
    if [ $? -ne 0 ]; then
      echo "Failed repairing wheel with auditwheel"
      exit 1;
    fi
    mv "$staging_path"/*manylinux*.whl "$output_path"/
}

make_shadow_copy "$project_source" "$CONTAINER_WORKSPACE"
cleanup_workspace "$CONTAINER_WORKSPACE"
output_staging_path=$(mktemp -d -t output_staging-XXXXXX)
for i in "${python_versions_to_use[@]}"; do
    echo "Creating wheel for Python version: $i"
    build_path=$(mktemp -d -t unfixed_wheel_python-$i-XXXXXX)
    create_wheel "$CONTAINER_WORKSPACE" "$i" "$build_path"
    fixup_wheel "$build_path" "$output_staging_path"
done
for file in $output_staging_path/*manylinux*.whl; do
    echo ''
    echo '================================================================================'
    auditwheel show $file
    echo '================================================================================'
done
mv "${output_staging_path}"/*.whl "$output_path"/
echo 'Done building wheels for distribution'
