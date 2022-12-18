import setuptools

_deps = [
    "websocket-client>=1.4.2",
    "requests>=2.28.1",

]

setuptools.setup(
    name="hfspaces_api",
    version="0.1",
    author="Ugur Sahin",
    url="https://github.com/ugorsahin/hfspaces_api",
    license='MIT',
    description="Huggingface Spaces websocket API",
    packages=['hfspaces_api'],
    install_requires=_deps
)
