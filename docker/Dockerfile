ARG ROS_DISTRO=jazzy

FROM ros:${ROS_DISTRO}-ros-base

ARG ROS_DISTRO
ARG DEBIAN_FRONTEND=noninteractive
ARG USERNAME=robot
ARG USER_UID=1001
ARG USER_GID=1001

ENV ROS_DISTRO=${ROS_DISTRO} \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && apt-get install -y --no-install-recommends \
        bash-completion \
        ca-certificates \
        clang-format \
        cppcheck \
        curl \
        gcovr \
        git \
        lcov \
        linux-libc-dev \
        python3-colcon-common-extensions \
        python3-pip \
        python3-pytest \
        python3-rosdep \
        python3-venv \
        shellcheck \
        ros-${ROS_DISTRO}-ament-cmake-gtest \
        ros-${ROS_DISTRO}-joint-state-publisher \
        ros-${ROS_DISTRO}-launch-testing-ros \
        ros-${ROS_DISTRO}-robot-state-publisher \
        ros-${ROS_DISTRO}-ros-gz-bridge \
        ros-${ROS_DISTRO}-ros-gz-sim \
        ros-${ROS_DISTRO}-xacro \
    && rm -rf /var/lib/apt/lists/*

# The ROS base image also carries global Python packages. Patch those in place so
# an image-wide Trivy scan does not retain vulnerable setuptools/msgpack copies.
RUN python3 -m pip install \
        --break-system-packages \
        --no-cache-dir \
        --upgrade \
        "setuptools==78.1.1" \
        "msgpack==1.2.1" \
        "urllib3==2.8.0" \
    && python3 -c 'import importlib.metadata as m; assert m.version("setuptools") == "78.1.1"; assert m.version("msgpack") == "1.2.1"; assert m.version("urllib3") == "2.8.0"'

RUN python3 -m venv --system-site-packages /opt/ci-venv \
    && /opt/ci-venv/bin/python -m pip install \
        --no-cache-dir \
        --upgrade \
        "pip==26.2.1" \
        "setuptools==78.1.1" \
        "msgpack==1.2.1" \
        "urllib3==2.8.0" \
    && /opt/ci-venv/bin/python -m pip install \
        --no-cache-dir \
        pytest-cov==7.1.0 \
        PyYAML==6.0.3 \
        ruff==0.15.21 \
    && PIP_VENDOR_DIR="$(/opt/ci-venv/bin/python -c 'import pathlib, pip; print(pathlib.Path(pip.__file__).parent / "_vendor")')" \
    && MSGPACK_DIR="$(/opt/ci-venv/bin/python -c 'import msgpack, pathlib; print(pathlib.Path(msgpack.__file__).parent)')" \
    && PKG_RESOURCES_DIR="$(/opt/ci-venv/bin/python -c 'import pathlib, pkg_resources; print(pathlib.Path(pkg_resources.__file__).parent)')" \
    && URLLIB3_DIR="$(/opt/ci-venv/bin/python -c 'import pathlib, urllib3; print(pathlib.Path(urllib3.__file__).parent)')" \
    && VENDOR_DIR="$(/opt/ci-venv/bin/python -c 'import pathlib, setuptools; print(pathlib.Path(setuptools.__file__).parent / "_vendor")')" \
    && rm -rf \
        "${PIP_VENDOR_DIR}/msgpack" \
        "${PIP_VENDOR_DIR}/pkg_resources" \
        "${PIP_VENDOR_DIR}/urllib3" \
    && cp -a "${MSGPACK_DIR}" "${PIP_VENDOR_DIR}/msgpack" \
    && cp -a "${PKG_RESOURCES_DIR}" "${PIP_VENDOR_DIR}/pkg_resources" \
    && cp -a "${URLLIB3_DIR}" "${PIP_VENDOR_DIR}/urllib3" \
    && diff -qr "${MSGPACK_DIR}" "${PIP_VENDOR_DIR}/msgpack" \
    && diff -qr "${PKG_RESOURCES_DIR}" "${PIP_VENDOR_DIR}/pkg_resources" \
    && diff -qr "${URLLIB3_DIR}" "${PIP_VENDOR_DIR}/urllib3" \
    && PIP_PKG_RESOURCES="${PIP_VENDOR_DIR}/pkg_resources/__init__.py" \
    && PIP_PKG_RESOURCES="${PIP_PKG_RESOURCES}" VENDOR_DIR="${VENDOR_DIR}" /opt/ci-venv/bin/python -c 'import os, pathlib; path = pathlib.Path(os.environ["PIP_PKG_RESOURCES"]); text = path.read_text(); old = "os.path.join(os.path.dirname(os.path.dirname(__file__)), '\''setuptools'\'', '\''_vendor'\'')"; new = repr(os.environ["VENDOR_DIR"]); assert text.count(old) == 1; path.write_text(text.replace(old, new))' \
    && PIP_VENDOR_MANIFEST="${PIP_VENDOR_DIR}/vendor.txt" \
    && PIP_VENDOR_MANIFEST="${PIP_VENDOR_MANIFEST}" /opt/ci-venv/bin/python -c 'import os, pathlib, re; path = pathlib.Path(os.environ["PIP_VENDOR_MANIFEST"]); text, count = re.subn(r"(?m)^(\s*)urllib3==[^\s]+$", r"\g<1>urllib3==2.8.0", path.read_text()); assert count == 1; path.write_text(text)' \
    && PIP_BOM="${PIP_VENDOR_DIR}/bom.cdx.json" \
    && PIP_BOM="${PIP_BOM}" /opt/ci-venv/bin/python -c 'import json, os, pathlib; path = pathlib.Path(os.environ["PIP_BOM"]); data = json.loads(path.read_text()); fixes = {"msgpack": "1.2.1", "setuptools": "78.1.1", "urllib3": "2.8.0"}; [component.update({"version": fixes[component["name"]], "purl": "pkg:pypi/" + component["name"] + "@" + fixes[component["name"]]}) for component in data["components"] if component["name"] in fixes]; path.write_text(json.dumps(data, indent=2) + "\n")' \
    && PATCH_DIR="$(mktemp -d)" \
    && /opt/ci-venv/bin/python -m pip install \
        --no-cache-dir \
        --no-deps \
        --target "${PATCH_DIR}" \
        "jaraco.context==6.1.0" \
        "wheel==0.46.3" \
    && rm -rf \
        "${VENDOR_DIR}/jaraco/context.py" \
        "${VENDOR_DIR}/jaraco/context" \
        "${VENDOR_DIR}/jaraco.context-5.3.0.dist-info" \
        "${VENDOR_DIR}/jaraco_context-5.3.0.dist-info" \
        "${VENDOR_DIR}/wheel" \
        "${VENDOR_DIR}/wheel-0.45.1.dist-info" \
    && cp -a "${PATCH_DIR}/jaraco/context" "${VENDOR_DIR}/jaraco/" \
    && cp -a "${PATCH_DIR}/jaraco_context-6.1.0.dist-info" "${VENDOR_DIR}/" \
    && cp -a "${PATCH_DIR}/wheel" "${VENDOR_DIR}/" \
    && cp -a "${PATCH_DIR}/wheel-0.46.3.dist-info" "${VENDOR_DIR}/" \
    && rm -rf "${PATCH_DIR}" \
    && /opt/ci-venv/bin/python -m pip check \
    && PIP_VENDOR_DIR="${PIP_VENDOR_DIR}" /opt/ci-venv/bin/python -c 'import json, os, pathlib; from pip._vendor import msgpack, pkg_resources, urllib3; vendor = pathlib.Path(os.environ["PIP_VENDOR_DIR"]).resolve(); expected = {"msgpack": "1.2.1", "setuptools": "78.1.1", "urllib3": "2.8.0"}; versions = {component["name"]: component["version"] for component in json.loads((vendor / "bom.cdx.json").read_text())["components"] if component["name"] in expected}; assert versions == expected; assert msgpack.version == (1, 2, 1); assert urllib3.__version__ == "2.8.0"; assert all(pathlib.Path(module.__file__).resolve().is_relative_to(vendor) for module in (msgpack, pkg_resources, urllib3))' \
    && grep -qx 'Version: 6.1.0' "${VENDOR_DIR}/jaraco_context-6.1.0.dist-info/METADATA" \
    && grep -qx 'Version: 0.46.3' "${VENDOR_DIR}/wheel-0.46.3.dist-info/METADATA" \
    && VENDOR_DIR="${VENDOR_DIR}" python3 -c 'import importlib, os, pathlib, pkg_resources; import jaraco.text; vendor = pathlib.Path(os.environ["VENDOR_DIR"]).resolve(); modules = (importlib.import_module("setuptools._vendor.jaraco.context"), importlib.import_module("setuptools._vendor.jaraco.text"), importlib.import_module("setuptools._vendor.wheel")); assert all(pathlib.Path(module.__file__).resolve().is_relative_to(vendor) for module in modules)'

ENV PATH="/opt/ci-venv/bin:${PATH}"

RUN rosdep init 2>/dev/null || true

COPY src /tmp/robot-src

RUN rosdep update \
    && apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rosdep install \
        --from-paths /tmp/robot-src \
        --ignore-src \
        --rosdistro "${ROS_DISTRO}" \
        -r \
        -y \
    && rm -rf \
        /tmp/robot-src \
        /var/lib/apt/lists/*

RUN groupadd \
        --gid "${USER_GID}" \
        "${USERNAME}" \
    && useradd \
        --uid "${USER_UID}" \
        --gid "${USER_GID}" \
        --create-home \
        --shell /bin/bash \
        "${USERNAME}" \
    && mkdir -p /workspace \
    && chown -R \
        "${USERNAME}:${USERNAME}" \
        /workspace

WORKDIR /workspace

USER ${USERNAME}

CMD ["/bin/bash"]
