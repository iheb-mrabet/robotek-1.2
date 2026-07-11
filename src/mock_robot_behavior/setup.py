from setuptools import find_packages, setup

package_name = "mock_robot_behavior"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Mock Robot Maintainer",
    maintainer_email="developer@example.com",
    description="Python mission behavior and action server for the mock robot.",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "mission_manager = mock_robot_behavior.mission_manager:main",
        ],
    },
)
