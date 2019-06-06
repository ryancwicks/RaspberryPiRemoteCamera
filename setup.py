import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="remote_camera",
    version="0.0.1",
    author="Ryan Wicks",
    author_email="ryancwicks@gmail.com",
    description="A package that is used to access a picamera on a remote Raspberry Pi.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ryancwicks/RaspberryPiRemoteCamera",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_data={'remote_camera': [
        'template\\*',
        'static\\*',
    ]},
    install_requires=[
        'Flask',
        # 'picamera',
        'zmq',
        'pillow',
        'numpy',
    ],
    entry_points={
        'console_scripts': [
            'run_server=remote_camera:main'
        ],
    }
)
