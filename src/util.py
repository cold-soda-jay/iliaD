# -*- coding: utf-8 -*-
"""
Product of cold-soda-jay

Utilities for data downloading and processing
"""
import time
import datetime
import os
import re
import zipfile
import getpass
import csv
import json
import bs4
import requests
import cypter as cy

from texttable import Texttable

class Session():
    """Session to login to ilias and download files.

    Attributes
    ----------
    target_directory: str
        default dirctory to save the documents
    path_of_data: str
        path of user login data and target directory data
    path_of_course: str
        path of Json file which contains user marked courses

    """
    target_directory = '../data/'
    path_of_data = 'data.csv'
    path_of_course = 'course.json'

    def __init__(self, username=None, password=None):
        """
        Initiate the session and login to ilias.

        Attributes
        ----------
        user:str
            User name, in Format of 'uxxxx'
        password: str
            Password for login
        """
        if username and password:
            self.session = requests.Session()
            self.bs4_soup = self.login(username, password)

    def login(self, username, password):
        """
        Login to ilias and return bs4 object.

        input
        ---------

        user:str
            User name, in Format of 'uxxxx'
        password: str
            Password for login

        return
        --------
        :bs4.BeautifulSoup
        """
        payload = {"sendLogin": 1,
                   "idp_selection": "https://idp.scc.kit.edu/idp/shibboleth",
                   "target": "https://ilias.studium.kit.edu/shib_login.php",
                   "home_organization_selection": "Mit KIT-Account anmelden"}
        response = self.session.post(
            "https://ilias.studium.kit.edu/Shibboleth.sso/Login",
            data=payload)

        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form', attrs={'class': 'form2', 'method': 'post'})
        action = form['action']

        # parse and login
        credentials = {"_eventId_proceed": "", "j_username": username, "j_password": password}
        url = "https://idp.scc.kit.edu" + action

        response = self.session.post(url, data=credentials)

        html_doc = response.text

        soup = bs4.BeautifulSoup(html_doc, 'html.parser')
        relay_state = soup.find('input', attrs={'name': 'RelayState'})
        saml_response = soup.find('input', attrs={'name': 'SAMLResponse'})

        if not relay_state:
            print('Wrong credentials!')
            raise Exception('wrong credentials!')

        payload = {'RelayState': relay_state['value'],
                   'SAMLResponse': saml_response['value'],
                   '_eventId_proceed': ''}
        dashboard_html = self.session.post(
            "https://ilias.studium.kit.edu/Shibboleth.sso/SAML2/POST",
            data=payload).text

        return bs4.BeautifulSoup(dashboard_html, 'html.parser')

    def get_courses(self):
        """
        Extract courses items
        """
        a_tags = self.bs4_soup.find_all('a', class_='il_ContainerItemTitle')
        return [self.format_tag(a_tag) for a_tag in a_tags]
    

    def format_tag(self, a_tag):
        """
        extract all course name and thire href 
        """
        base_url = "https://ilias.studium.kit.edu/"

        href = a_tag["href"]
        if not re.match(base_url, href):
            href = base_url + href

        return {"name": a_tag.contents[0], "href": href}

    def download(self, courses, target=None):
        """
        Download all marked courses and save them into target directory
        
        Attribute
        ---------
        courses: dict
            A dictionary of courses.
        target: str
            The path of target directory

        Return
        --------
            :list of new added file

        """
        if target:
            self.target_directory = target
        percent = 0
        new_file_list = ''
        print('Downloading...')
        part = 1 / len(courses)
        for course in courses:
            print('\r',
                  '[ ' + '#' * int(percent * 30) + '>' + '%.2f'%(percent * 100) + '%' + ' ' * (
                      30 - int(percent * 30)),
                  end=' ]', flush=True)
            link = course["href"]
            course_name = course['name']
            if '/' in course_name:
                course_name = course_name.replace('/', '&&')

            try:
                os.mkdir(self.target_directory + course_name)
            except:
                pass
            new_file_list+='\n# %s\n'%course_name
            html = self.session.get(link).text
            soup = bs4.BeautifulSoup(html, 'html.parser')
            ziplist = soup.find_all('span', class_='xsmall')
            if len(ziplist) == 0:
                continue
            subpart = 1 / len(ziplist)
            for item in ziplist:
                print('\r',
                      '[ ' + '#' * int(percent * 30) + '>' + '%.2f'%(percent * 100) + '%' + ' ' * (
                          30 - int(percent * 30)),
                      end=' ]', flush=True)

                if item.text == 'Download':
                    zipurl = item.parent.attrs['href']
                    download_cache = self.session.get("https://ilias.studium.kit.edu/" + zipurl)
                    with open(self.target_directory + course_name + '/cache.zip', 'wb') as f:
                        f.write(download_cache.content)

                    with zipfile.ZipFile(self.target_directory + course_name + '/cache.zip', 'r') as z:
                        zippart = 1 / len(z.namelist())
                        cache_folder=''
                        for file_name in z.namelist():
                            print('\r',
                                  '[ ' + '#' * int(percent * 30) +
                                  '>' + '%.2f'%(percent * 100) + '%' + ' ' * (
                                      30 - int(percent * 30)),
                                  end=' ]', flush=True)
                            if os.path.isfile(self.target_directory + course_name+'/'+file_name):
                                continue
                            z.extract(file_name, self.target_directory + course_name)
                            if file_name.endswith('/') and file_name.count('/')==1:
                                new_file_list+='%s~ %s\n'%(4*' ', file_name)
                                cache_folder=file_name
                            else:
                                new_file_list+='%s- %s\n'%(8*' ', file_name.replace(cache_folder,''))

                            percent += part * subpart * zippart
                    os.remove(self.target_directory + course_name + '/cache.zip')
                else:
                    percent += part * subpart
        percent = 1
        print('\r',
              '[ ' + '#' * int(percent * 30) + '>' + '%.2f'%(percent * 100) + '%' + ' ' * (
                  30 - int(percent * 30)),
              end=' ]', flush=True)
        print('\nDone!')
        return new_file_list

    def get_marked_course_list(self, choose=False):
        """
        Get marked courses from course.json. If the file not exist, then choose the course.

        return
        -------
        marked_course:list
        """
        if choose:
            marked_course = self.choose_course()
            return marked_course
        try:
            with open(self.path_of_course, "r") as file:
                marked_course = json.loads(file.read())
            return marked_course
        except:
            print('No Marked Course!')
            marked_course = self.choose_course()
            return marked_course

    def choose_course(self):
        """
        Choose the course to download
        """
        raw_list = self.get_courses()
        t = Texttable()
        table=[["Nr.", "Course"]]
        i = 1
        for course in raw_list:
            table.append([i,course['name']])
            i += 1
        t.add_rows(table)
        dialog=True
        print(t.draw())
        while dialog:
            confirm=True
            marked = []
            numbers = input('Choose couses by typing the number of course, separate with \' , \' :')
            for num in numbers.split(','):
                try:
                    if raw_list[int(num)-1] not in marked:
                            marked.append(raw_list[int(num)-1])
                            print('%s. %s'%(str(len(marked)),raw_list[int(num)-1]['name']))
                except:
                    print('Ivalid input!: %s'%num)
                    confirm = False
                    break

            while confirm:
                answer=input('\nThoses are choosed courses.\nConfirm?(y/n)')
                if answer=='y':
                    dialog=False
                    break
                elif answer!='n':
                    print('Ivalid input!')
                    continue
                break
        with open(self.path_of_course, "w") as file:
            json.dump(marked, file)
        print('\nSaved to %s!\n'%self.path_of_course)    
        return marked


class Synchronizer:
    """
    A synchronizer which allows user to login ,download, check user data
    """
    path_of_data = 'data.csv'

    def init_login_data(self, user=None, target=None, password=False):
        """
        Initiate login data
        """
        if password:
            pwd = getpass.getpass("Please give password(Pw won't show in Terminal): ")
            self.write_user_data('pwd',pwd)
            return None
        if not user:
            user = input('Please give username (U-Account):\n')
            if target == 'ch':
                self.write_user_data('user',user)
                return None
        if not target:
            target = input('Please give target directory:\n')
            if user == 'ch':
                self.write_user_data('target', target)
                return None

        if not (target.endswith('\\') or target.endswith('/')):
            target+='/'
        with open(self.path_of_data, 'w', newline='', encoding='utf-8') as csvfile:
            spamwriter = csv.writer(csvfile)
            spamwriter.writerow(['key','value'])
        pwd = getpass.getpass("Please give password(Pw won't show in Terminal): ")
        with open(self.path_of_data, "a+") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['user',user])
            writer.writerow(['pwd',cy.enCode(pwd)])
            writer.writerow(['target',target.replace('\\','/')])
        return pwd

    def synchronize(self):
        startt = time.time()
        try:
            session, target = self.login()
        except:
            return
        
        print('%s: Login succeed!'%(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        courslist = session.get_marked_course_list()
        print('%s: Checking courses...'%(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        new_file_list = session.download(courslist,target)
        print('Time coast:%.2f\n%s: New files:'%((time.time()-startt),
                                                 (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
        print(new_file_list)

    def login(self):
        user = ''
        pwd = ''
        target = ''
        try:
            with open(self.path_of_data, 'rt', encoding='utf-8') as fp:
                reader = csv.DictReader(fp)
                for row in reader:
                    if row['key'] == 'target':
                        target = row['value']
                    elif row['key'] == 'user':
                        user = row['value']
                    elif row['key'] == 'pwd':
                        pwd = cy.deCode(row['value'])
            if user == '' or pwd == '' or target == '':
                print('No Data!')
                print('Please initialize user configuration at first!!\n')
                return None
            session = Session(username=user, password=pwd)
            return session, target
        except:
            print('No Data!')
            print('Please initialize user configuration at first!!\n')
            return None

    def show_user_data(self):
        try:
            with open(self.path_of_data, 'rt', encoding='utf-8') as fp:
                reader = csv.DictReader(fp)
                for row in reader:
                    if row['key'] == 'target':
                        target = row['value']
                    elif row['key'] == 'user':
                        user = row['value']
                    elif row['key'] == 'pwd':
                        pwd = cy.deCode(row['value'])
            if user == '' or pwd == '' or target == '':
                print('No Data!')
                print('Please initialize user configuration at first!!')
                return None
            print('\nusername: %s\n\nTarget folder: %s\n'%(user,target))
            while True:
                answer = input('Do you want to check password?\n(y/n)')
                if answer =='y':
                    npwd = getpass.getpass("Please give password to check if the stored pw right (Pw won't show in Terminal): ")
                    if pwd==npwd:
                        print("\nPassword match!")
                    else:
                        print('\nPassword dosen\'t match!')
                elif answer !='n':
                    print('Ivalid input!')
                    continue
                break
            while True:
                change_question = input('Do you want to edit user name, target directory or password?\n(y/n)')
                if change_question == 'y':
                    while True:
                        yChange = input('Which one do you want to change?\n\n1. User name\n2. Target directory\n3. Password\n4. All\n5. Cancel\n')
                        if yChange == '1':
                            self.init_login_data(target='ch')
                        elif yChange == "2":
                            self.init_login_data(user='ch')
                        elif yChange == "3":
                            self.init_login_data(password=True)
                        elif yChange == "4":
                            self.init_login_data()
                        elif yChange == "5":
                            return
                        else:
                            print('Ivalid input!')
                            continue
                        while True:
                            cont=input('Do you want to edit anything else?\n(y/n)')
                            if cont == 'y':
                                break
                            elif cont == 'n':
                                return
                            else:
                                print('Ivalid input!')
                                continue
                elif change_question != 'n':
                    print('Ivalid input!')
                    continue
                break
        except:
            print('No Data!')
            print('Please initialize user configuration at first!!\n')
            return None

    def show_marked_course(self):
        try:
            session, target = self.login()
        except:
            return
        clist=session.get_marked_course_list(choose=False)
        out='\nChoosed courses:\n'
        if clist is None:
            return
        for counter, value in enumerate(clist):
            out+='\n%s: %s\n'%(str(counter+1),value['name'])
        print(out)
        while True:
            answer=input('Do you want to edit course list?\n(y/n)')
            if answer == 'y':
                self.change_marked_course()
            elif answer != 'n':
                print('Ivalid input!')
                continue
            break

    def change_marked_course(self):
        session, target = self.login()
        session.choose_course()

    def write_user_data(self,key, value):
        csvdict = csv.DictReader(open(self.path_of_data, 'rt', encoding='utf-8', newline=''))
        dictrow = []
        for row in csvdict:
            if row['key'] == key:
                row['value'] = value
            # rowcache.update(row)
            dictrow.append(row)

        with open(self.path_of_data, "w+", encoding='utf-8', newline='') as lloo:
            # lloo.write(new_a_buf.getvalue())
            wrier = csv.DictWriter(lloo, ['key', 'value'])
            wrier.writeheader()
            for wowow in dictrow:
                wrier.writerow(wowow)

