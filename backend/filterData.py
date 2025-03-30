import os
import logging
from lxml import etree
import pandas as pd
from collections import defaultdict

# Configure logging
logging.basicConfig(filename="filter_data.log", level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def filterData():
    try:
        # Define types and fields to exclude
        excluded_types = {"HKQuantityTypeIdentifierHeadphoneAudioExposure", "HKCategoryTypeIdentifierHeadphoneAudioExposureEvent", "HKQuantityTypeIdentifierEnvironmentalAudioExposure"}
        excluded_columns = {"sourceName", "sourceVersion", "device"}

        records_by_type = defaultdict(list)

        # Create a forgiving XML parser using lxml with recover=True
        parser = etree.XMLParser(recover=True)
        xml_path = "appleHealth/uploadData.xml"
        try:
            with open(xml_path, "rb") as f:
                tree = etree.parse(f, parser)
                root = tree.getroot()
                for elem in root.iter("Record"):
                    record_type = elem.attrib.get("type")
                    # Skip records with excluded types or all category type identifiers
                    if record_type and "HKCategoryTypeIdentifier" not in record_type and record_type not in excluded_types:
                        # Remove the common prefix to create a short type name
                        short_type = record_type.replace("HKQuantityTypeIdentifier", "")
                        # Collect attributes, excluding specified columns
                        clean_record = {k: v for k, v in elem.attrib.items() if k not in excluded_columns}
                        clean_record["type"] = short_type  # Overwrite full type with short type
                        records_by_type[short_type].append(clean_record)
        except etree.XMLSyntaxError as e:
            logger.error(f"XML Parsing Error: {e}")
            raise

        # Create export directory if it doesn't exist
        os.makedirs("export", exist_ok=True)

        # Export each record type to its own CSV file only if there are at least 100 records
        for short_type, records in records_by_type.items():
            if len(records) > 100:
                df = pd.DataFrame(records)
                csv_filename = f"export/{short_type.lower()}.csv"
                df.to_csv(csv_filename, index=False)
                logger.info(f"Exported {csv_filename} with {len(records)} records.")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise


if __name__ == "__main__":
    filterData()