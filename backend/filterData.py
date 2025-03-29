import os
import logging
import xml.etree.ElementTree as ET
import pandas as pd
from collections import defaultdict

# Configure logging
logging.basicConfig(
    filename='filter_data.log',  # Log file name
    level=logging.DEBUG,         # Log level
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def filterData():
    try:
        # Define types and fields to exclude
        excluded_types = {
            "HKQuantityTypeIdentifierHeadphoneAudioExposure",
            "HKCategoryTypeIdentifierHeadphoneAudioExposureEvent",
            "HKQuantityTypeIdentifierEnvironmentalAudioExposure"
        }
        excluded_columns = {"sourceName", "sourceVersion", "device"}

        records_by_type = defaultdict(list)

        # Parse the XML file with error handling
        try:
            for event, elem in ET.iterparse("appleHealth/uploadData.xml", events=("end",)):
                if elem.tag == "Record":
                    record_type = elem.attrib.get("type")

                    # Skip excluded types
                    if record_type and "HKCategoryTypeIdentifier" not in record_type and record_type not in excluded_types:
                        short_type = record_type.replace("HKQuantityTypeIdentifier", "")
                        clean_record = {k: v for k, v in elem.attrib.items() if k not in excluded_columns}
                        clean_record["type"] = short_type  # Overwrite long type
                        records_by_type[short_type].append(clean_record)

                elem.clear()
        except ET.ParseError as e:
            logger.error(f"XML Parsing Error: {e}")
            raise  # Re-raise the exception after logging

        # Create export directory if it doesn't exist
        os.makedirs("export", exist_ok=True)

        # Write CSV files for each record type
        for short_type, records in records_by_type.items():
            if len(records) > 100:
                df = pd.DataFrame(records)
                csv_filename = f"export/{short_type.lower()}.csv"
                df.to_csv(csv_filename, index=False)
                logger.info(f"Exported {csv_filename} with {len(records)} records.")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the exception after logging
