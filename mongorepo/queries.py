from typing import Literal

Operation = Literal[
    '$set',          # Set value
    '$push',         # Append to an array
    '$incr',         # Increment value
    '$pull',         # Remove an element from an array
    '$each',         # Apply operation to each element
    '$sort',         # Sort elements
    '$slice',        # Slice elements
    '$addToSet',     # Add unique values to an array
    '$pop',          # Remove first or last element
    '$rename',       # Rename a field
    '$unset',        # Remove a field
    '$currentDate',  # Set the field to the current date
    '$min',          # Update to a minimum value if specified value is less
    '$max',          # Update to a maximum value if specified value is more
    '$mul',          # Multiply a field value by a number
]

Condition = Literal[
    '$and',          # Logical AND
    '$or',           # Logical OR
    '$not',          # Logical NOT
    '$nor',          # Logical NOR
    '$exists',       # Field existence check
    '$type',         # Type check for field
    '$in',           # Field value is in array
    '$nin',          # Field value is not in array
    '$eq',           # Equals
    '$ne',           # Not equals
    '$gt',           # Greater than
    '$gte',          # Greater than or equal
    '$lt',           # Less than
    '$lte',          # Less than or equal
    '$regex',        # Regular expression match
    '$all',          # Array contains all elements
    '$elemMatch',    # Match elements in an array field
    '$size',         # Match array size
]


AggregationStage = Literal[
    '$match',          # Filters documents
    '$group',          # Groups documents by a specified expression
    '$sort',           # Sorts documents by a specified field
    '$project',        # Selects which fields to include or exclude
    '$limit',          # Limits the number of documents
    '$skip',           # Skips a specified number of documents
    '$unwind',         # Deconstructs an array field to output one document per element
    '$lookup',         # Performs a join with another collection
    '$facet',          # Processes multiple pipelines within a single stage
    '$count',          # Counts the number of documents
    '$addFields',      # Adds new fields to documents
    '$replaceRoot',    # Replaces the root document with a specified sub-document
    '$bucket',         # Categorizes documents into buckets
    '$bucketAuto',     # Categorizes documents into auto-generated buckets
    '$geoNear',        # Sorts documents by proximity to a specified point
]

UpdateModifier = Literal[
    '$inc',            # Increments a field by a specified value
    '$mul',            # Multiplies the value of a field by a specified number
    '$rename',         # Renames a field
    '$setOnInsert',    # Sets a field if document is inserted
    '$set',            # Sets the value of a field
    '$unset',          # Removes a field from a document
    '$min',            # Only updates the field if the specified value is less
    '$max',            # Only updates the field if the specified value is greater
    '$currentDate',    # Sets the value of a field to the current date
    '$addToSet',       # Adds value to an array if it doesn’t exist
    '$push',           # Appends a value to an array
    '$pull',           # Removes elements from an array that match a condition
    '$pullAll',        # Removes all instances of specified values from an array
    '$pop',            # Removes the first or last item of an array
    '$bit',            # Performs bitwise operations on integer values
]
