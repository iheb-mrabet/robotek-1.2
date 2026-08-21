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
    && python3 -c 'import importlib.metadata as m; assert m.version("setuptools") == "78.1.1"; assert m.version("msgpack") == "1.2.1"'

RUN python3 -m venv --system-site-packages /opt/ci-venv \
    && /opt/ci-venv/bin/python -m pip install \
        --no-cache-dir \
        --upgrade \
        pip \
        "setuptools==78.1.1" \
        "msgpack==1.2.1" \
    && /opt/ci-venv/bin/python -m pip install \
        --no-cache-dir \
        pytest-cov==7.1.0 \
        PyYAML==6.0.3 \
        ruff==0.15.21 \
    && VENDOR_DIR="$(/opt/ci-venv/bin/python -c 'import pathlib, setuptools; print(pathlib.Path(setuptools.__file__).parent / "_vendor")')" \
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
