import lxml.etree as ET

class ead(object):
    '''Encoded Archival Description object'''
    def __init__(self, id, handle, xmlfile):
        self.name = id
        self.tree = ET.parse(xmlfile)
        self.handle = handle

'''
    #===========================
    # fix incorrect box numbers
    #===========================
    def fix_box_number_discrepancies(root):
        boxes = [c for c in root.iter('container') if c.get('type') == 'box']
        for box in boxes:
            match = re.search(r'^(box)?(\d+).\d+$', box.get('id'))
            if box.text != match.group(2):
                box.text = match.group(2)
                logging.info('Corrected box {0} to {1}'.format(
                    ET.tostring(box), match.group(2)))
        return root


    #=================================
    # Add box containers where absent
    #=================================
    def add_missing_box_containers(root):
        # iterate over item- and file-level containers
        for n, did in enumerate(root.iter('did')):
            parent = did.getparent()
            parent_level = parent.get('level')

            if parent_level in ['file', 'item']:
                # check whether a box container exists already; if so, break out
                for c in did.iterchildren(tag='container'):
                    if c.get('type') == 'box':
                        break
                # if not, create a box container
                else:
                    box_attribute = c.get('parent')
                    match = re.search(r'^(box)?(\d+).(\d+)$', box_attribute)

                    # create attributes corresponding to the parent box
                    if match:
                        box_number = match.group(2)
                        box_id = "{0}.{1}".format(match.group(2), match.group(3))
                        new_container = ET.SubElement(did, "container")
                        new_container.set('type', 'box')
                        new_container.set('id', box_id)
                        new_container.text = box_number
                    
        return root


    #======================================
    # Missing extents in physdesc elements
    #======================================
    def add_missing_extents(root):
        for physdesc in root.findall('physdesc'):
            children = physdesc.getchildren()
            if "extent" not in children:
                ext = ET.SubElement(physdesc, "extent")
                ext.text = physdesc.text
                physdesc.text = ''
                logging.info('Added missing extent element to {0}'.format(physdesc))
        return root


    #=============================
    # Add title attribute to dao
    #=============================
    def add_title_to_dao(root):
        for dao in root.findall('dao'):
            parent = dao.getparent()
            unittitle = parent.find('unittitle').text
            if unittitle:
                dao.set('title', unittitle)
            else:
                logging.warn('Cannot find unittitle for dao element')
        return root


    #==================================================
    # Remove elements containing only empty paragraphs
    #==================================================
    def remove_empty_elements(root):
        node_types = ['bioghist', 'processinfo', 'scopecontent']
        # check for each of the three elements above
        for node_type in node_types:
            # iterate over instances of the element
            for node in root.findall(node_type):
                parent = node.getparent()
                # find all the paragraphs in the node
                paragraphs = node.findall('p')
                # if any contain text, break the loop
                for p in paragraphs:
                    if len(p) > 0 or p.text is not None:
                        break
                # otherwise remove the parent element
                else:
                    logging.info(ET.tostring(instance))
                    parent.remove(instance)
        return root


    #==============================
    # Remove "Guide to" from title
    #==============================
    def remove_opening_of_title(root):
        titleproper = root.find('titleproper')
        # if title.text begins with "Guide to", remove it and capitalize next word
        if titleproper is not None and titleproper.text is not '':
            titleproper_old = titleproper.text

            if titleproper_old is not None and titleproper_old.startswith(
                                                                    "Guide to"):

                titleproper_new = titleproper_old[9].upper() + titleproper_old[10:]

                if len(titleproper_new) > 25:
                    new_t = titleproper_new[:25] + "..."
                    old_t = titleproper_old[:25] + "..."
                else:
                    new_t = titleproper_new
                    old_t = titleproper_old
                
                print("  Altered title: {0} => {1}".format(old_t, new_t))

        return root


    #======================================================
    # Move scope and content section from analytic cover to 
    #======================================================
    def move_scopecontent(root):
        analyticover = root.xpath('//dsc[@type="analyticover"]')
    
        # iterate over scope and content notes inside analytic cover section
        for ac in analyticover:
            for sc in ac.iter('scopecontent'):
                paragraphs = [node for node in sc if node.tag is 'p']

                for p in paragraphs:
                    if p.text is not None:
                        break # move the content over

            ac.getparent().remove(ac)

        return root


    #=================================================
    # Remove alternative abstracts used for ArchivesUM
    #=================================================
    def remove_multiple_abstracts(root):
        abstracts = [a for a in root.iter('abstract')]

        print("  Found {0} abstracts:".format(len(abstracts)))

        if len(abstracts) > 1:
            for abstract_num, abstract in enumerate(abstracts):
                label = abstract.get('label')

                if label == "Short Description of Collection":
                    print("    {0}. Keeping Short Description".format(
                                                        abstract_num +1))
                else:
                    print("    {0}. Removing abstract '{1}'...".format(
                                                        abstract_num + 1, label))
                    abstract.getparent().remove(abstract)
        else:
            print("  There is only one abstract.")
        
        return root


    #=================================================
    # Add handle uri as an attribute of the eadid elem
    #=================================================
    def insert_handle(root, handle):
        eadid = root.find('.//eadid')
        eadid.set('url', handle)
        return root
'''

