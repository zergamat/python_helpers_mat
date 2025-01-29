from setuptools import setup, find_packages

setup(
    name='python_helpers_mat',  # Nazwa pakietu
    version='0.1.0',  # Wersja pakietu
    description='Helper functions',
    long_description=open('README.md').read(),  # Długi opis z pliku README.md
    long_description_content_type='text/markdown',  # Typ opisu (markdown)
    author='zergamat',
    author_email='zergamat@gmail.com',
    url='https://github.com/zergamat/python_helpers_mat.git',  # Adres URL projektu na GitHubie
    packages=find_packages(),  # Automatyczne znajdowanie pakietów
    install_requires=[
        # Lista zależności (jeśli istnieją)
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',  # Status rozwoju
        'Intended Audience :: Developers',  # Odbiorcy
        'License :: OSI Approved :: MIT License',  # Licencja
        'Programming Language :: Python :: 3',  # Wersja Pythona
    ],
)
