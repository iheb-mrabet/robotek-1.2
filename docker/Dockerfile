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

RUN python3 -m venv --system-site-packages /opt/ci-venv \
    && /opt/ci-venv/bin/python -m pip install \
        --no-cache-dir \
        --upgrade \
        pip \
    && /opt/ci-venv/bin/python -m pip install \
        --no-cache-dir \
        pytest-cov==7.1.0 \
        PyYAML==6.0.3 \
        ruff==0.15.21 \
    && /opt/ci-venv/bin/python -m pip check

ENV PATH="/opt/ci-venv/bin:${PATH}"

RUN rosdep init 2>/dev/null || true

COPY src /tmp/robot-src

RUN rosdep update \
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