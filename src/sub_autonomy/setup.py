from setuptools import find_packages, setup

package_name = 'sub_autonomy'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='robosub',
    maintainer_email='kbenton4001@gmail.com',
    description='autonsub',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        'sub_controller = sub_autonomy.sub_controller:main',   
        'mission_executor = sub_autonomy.mission_executor:main',
        ],
    },
)
