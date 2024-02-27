python_sources(name="lib")

resources(name="py.typed", sources=["py.typed"])

python_distribution(
    name="dist",
    dependencies=[":lib", ":py.typed"],
    wheel=True,
    sdist=True,
    provides=setup_py(
        name="era_5g_heartbeat",
        version="0.2.0",
        description="Heartbeat module for 5G ERA applications.",
        author="Petr Kleparnik",
        author_email="p.kleparnik@cognitechna.cz",
        license="LGPL",
        python_requires=">=3.8",
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
            "Operating System :: OS Independent",
            "Intended Audience :: Developers",
        ],
    ),
)
