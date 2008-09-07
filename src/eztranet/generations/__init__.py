from zope.app.generations.generations import SchemaManager

# minimum generation is the number to which the database will automatically
# evolve at startup.

# generation is the max generation known to the manager,ie the generation of the
# current version

EztranetSchemaManager = SchemaManager(
    minimum_generation=0,
    generation=0,
    package_name='eztranet.generations'
)

