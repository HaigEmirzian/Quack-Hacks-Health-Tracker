import xml.etree.ElementTree as ET
import pandas as pd
import os
from collections import defaultdict

# Types to exclude entirely
excluded_types = {"HKQuantityTypeIdentifierHeadphoneAudioExposure", "HKCategoryTypeIdentifierHeadphoneAudioExposureEvent", "HKQuantityTypeIdentifierEnvironmentalAudioExposure"}

# Fields to exclude from each record
excluded_columns = {"sourceName", "sourceVersion", "device"}

records_by_type = defaultdict(list)

# Efficient streaming XML parser
for event, elem in ET.iterparse("export.xml", events=("end",)):
    if elem.tag == "Record":
        record_type = elem.attrib.get("type")

        # Skip category types and specific excluded types
        if record_type and "HKCategoryTypeIdentifier" not in record_type and record_type not in excluded_types:
            # Strip identifier prefix from type
            short_type = record_type.replace("HKQuantityTypeIdentifier", "")

            # Filter out unused fields
            clean_record = {k: v for k, v in elem.attrib.items() if k not in excluded_columns}
            clean_record["type"] = short_type  # overwrite long type

            # Store by short type
            records_by_type[short_type].append(clean_record)

    elem.clear()

# Write one CSV per metric if it has more than 100 records
os.makedirs("export", exist_ok=True)

for short_type, records in records_by_type.items():
    if len(records) > 100:
        df = pd.DataFrame(records)
        df.to_csv(f"export/{short_type.lower()}.csv", index=False)
