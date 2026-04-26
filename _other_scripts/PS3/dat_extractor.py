import csv
from lxml import etree

def xml_to_flat_csv(xml_input, csv_output):
    # Defining headers to match your desired output exactly
    headers = [
        'game_name', 'id', 'category', 'description',
        'game_id', 'rom_name', 'size', 'crc', 'md5', 'sha1', 'sha256'
    ]

    with open(csv_output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        # Stream the XML file
        context = etree.iterparse(xml_input, events=('end',), tag='game')

        for event, elem in context:
            # 1. Capture the main Game attributes and child tags
            # elem.get() is for attributes (name="..."), elem.findtext() is for <tag>...</tag>
            base_game_info = {
                'game_name': elem.get('name'),
                'id': elem.get('id'),
                'category': elem.findtext('category'),
                'description': elem.findtext('description'),
                'game_id': elem.findtext('game_id')  # This captures the JP0745... text
            }

            # 2. Look for all <rom> tags inside this <game>
            roms = elem.findall('rom')

            if roms:
                for rom in roms:
                    row = base_game_info.copy()
                    # Add ROM-specific attributes
                    row.update({
                        'rom_name': rom.get('name'),
                        'size': rom.get('size'),
                        'crc': rom.get('crc'),
                        'md5': rom.get('md5'),
                        'sha1': rom.get('sha1'),
                        'sha256': rom.get('sha256')
                    })
                    writer.writerow(row)
            else:
                # Still write the game if no ROMs exist
                writer.writerow(base_game_info)

            # 3. Clean up memory
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]

# Run the process
xml_to_flat_csv('ps3_psn_dlc.xml', 'app_ps3_dlc.csv')