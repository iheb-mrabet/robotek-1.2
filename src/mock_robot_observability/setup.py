from setuptools import find_packages, setup

package_name = "mock_robot_observability"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        (
            "share/ament_index/resource_index/packages",
            ["resource/" + package_name],
        ),
        (
            "share/" + package_name,
            ["package.xml"],
        ),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Iheb Mrabet",
    maintainer_email="iheb.mrabet@example.com",
    description="ROS 2 Prometheus exporter for Robotek.",
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "ros_exporter = mock_robot_observability.exporter:main",
        ],
    },
)
