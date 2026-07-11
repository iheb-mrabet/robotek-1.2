from setuptools import find_packages, setup

package_name = "mock_robot_system_tests"

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
    description="Launch, integration, and headless simulation tests for the mock robot.",
    license="Apache-2.0",
    tests_require=["pytest"],
)
