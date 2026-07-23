from setuptools import find_packages, setup

setup(
    name='netbox-ixc-sync',
    version='0.1.0',
    description='Plugin NetBox para sincronizar clientes e IPs fixos do IXCSoft',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/SEU_USUARIO/netbox-ixc-sync',
    author='Nicfibra',
    license='MIT',
    install_requires=['requests'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
