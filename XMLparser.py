import os
import xml.etree.ElementTree as ET
import time

# Document folder path
dir_path = r'./XML'

# List to store files
file_names = []

# Iterate directory, populate list of files
print('Gathering files...')
filecount = 0
for path in os.listdir(dir_path):
    # check if current path is a file
    if os.path.isfile(os.path.join(dir_path, path)):
        file_names.append(path)
        filecount += 1
print(f'Found {filecount} files.')

parse_time = time.time()
print(f'Parsing files...')
for file_name in file_names: # For each file found...
    print(f'{file_name}')
    # Open the file and get the element tree
    file = open(dir_path + '/' + file_name, 'r', encoding='utf-8') # UTF-8 to allow 'special characters'
    tree = ET.parse(file)
    root = tree.getroot()
    table = []

    # ------- Works Every Time! ------- #
    # Append name;;;;<Author> to table
    for ele in root.iter('contrib'):
        contrib_type = ele.get('contrib-type')
        if contrib_type == 'author':
            name_ele = ele.find('name')

            surname_ele = name_ele.find('surname')
            given_names_ele = name_ele.find('given-names')

            name = surname_ele.text + " " + given_names_ele.text
            table.append('name;;;;' + name)
    
    # Append aff;;;;<Affiliation> to table
    for ele in root.iter('aff'):
        aff = ''
        end = ''
        for child in ele.iter():
            if child.tag == 'bold' or child.tag == 'institution-id' or child.tag == 'label':
                continue
            if child.tag == 'institution-wrap' and child.tail != None:
                end = child.tail
            if child.text != None:
                aff += child.text + ' '
        table.append('aff;;;;' + aff.strip() + end)
    
    # ------- Works Consistently(?) ------- #
    # Append element-citation;;;;<Citation> to table
    for ele in root.iter('element-citation'):
        citation = ''
        for ele_cit in ele.iter():
            group = ele_cit.find('person-group')
            if group != None:
                for person in group.iter('name'):
                    citation += ' '
                    surname_ele = person.find('surname')
                    citation += surname_ele.text + ' '
                    given_names_ele = person.find('given-names')
                    for c in given_names_ele.text:
                        citation += c
                    citation += ' '

            title = ele_cit.find('article-title')
            if title != None:
                citation += '  '
                for title_parts in title.iter():
                    if title_parts.tag == 'named-content':
                        citation += ' ' + title_parts.text.strip('\n\t') + ' '
                    elif title_parts.tag == 'italic':
                        citation += title_parts.text.strip('\n\t') + ' '
                    else:
                        citation += title_parts.text.strip('\n\t')
                    if title_parts.tail != None:
                        citation += title_parts.tail.strip('\n')
                citation += ' '
            
            source = ele_cit.find('source')
            if source != None:
                citation += source.text
                citation += ' '

            year = ele_cit.find('year')
            if year != None:
                citation += year.text + ' '
            
            volume = ele_cit.find('volume')
            if volume != None:
                citation += volume.text
                citation += ' '

            fpage = ele_cit.find('fpage')
            if fpage != None:
                    citation += fpage.text
                    citation += ' '
            lpage = ele_cit.find('lpage')
            if lpage != None:
                    citation += lpage.text
                    citation += ' '
            pubid = ele_cit.find('pub-id')
            if pubid != None:
                    citation += pubid.text
                    citation += ' '
            
        table.append("element-citation;;;;" + citation.strip(' '))
    
    # No occurances to test so far
    # Append mixed-citation;;;;<Citation> to table
    for ele in root.iter('mixed-citation'):
        citation = ''

        # Citation Type = Other
        for child in ele.iter():
            if child.text != None:
                citation += child.text
            if child.tail != None:
                citation += child.tail

        table.append("mixed-citation;;;;" + citation)
    
    # Write table to a file
    if not table:
        print(f'File {file_name} had no data!')
        continue
    file_name_noex = file_name.partition('.')[0] # Assumes there is only one . in file name
    tfname = './Tables/' + file_name_noex + '_TABLE.txt'
    try:
        tfile = open(tfname, 'x', encoding='utf-8')
    except:
        tfile = open(tfname, 'w', encoding='utf-8')
    
    tfile.write(table[0])
    for entry in table[1:]:
        tfile.write('\n' + entry)
    tfile.close()

parse_time = time.time() - parse_time
print(f'Done in {parse_time} seconds.')
