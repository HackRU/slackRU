import requests
from pprint import pprint

# tags = requests.get('https://api.stackexchange.com/2.2/tags?page=1&pagesize=100&order=desc&sort=popular&site=stackoverflow')
# items = tags.json()['items']
# all_tags_1 = [t['name'] for t in items] 

# tags = requests.get('https://api.stackexchange.com/2.2/tags?page=2&pagesize=100&order=desc&sort=popular&site=stackoverflow')
# items = tags.json()['items']
# all_tags_2 = [t['name'] for t in items]

# all_tags = all_tags_1 + all_tags_2 
# print(all_tags)

all_tags = ['javascript', 'java', 'c#', 'php', 'android', 'jquery', 'python', 'html', 'c++',
 'ios', 'css', 'mysql', 'sql', 'asp.net', 'ruby-on-rails', 'objective-c', 'c', '.net',
  'arrays', 'angularjs', 'json', 'sql-server', 'r', 'iphone', 'node.js', 'ruby', 'ajax',
   'regex', 'swift', 'xml', 'asp.net-mvc', 'django', 'linux', 'database', 'excel', 'wpf',
    'wordpress', 'spring', 'string', 'xcode', 'windows', 'vb.net', 'eclipse', 'html5',
     'multithreading', 'git', 'bash', 'angular', 'mongodb', 'vba', 'oracle', 'twitter-bootstrap',
      'forms', 'python-3.x', 'image', 'macos', 'algorithm', 'facebook', 'postgresql', 'laravel',
       'python-2.7', 'winforms', 'apache', 'matlab', 'visual-studio', 'scala', 'performance',
        'entity-framework', 'excel-vba', 'list', 'css3', 'reactjs', 'swing', 'hibernate', 'linq',
         'qt', 'function', 'shell', '.htaccess', 'rest', 'pandas', 'api', 'sqlite', 'maven', 'perl',
          'codeigniter', 'web-services', 'file', 'google-maps', 'ruby-on-rails-3', 'cordova',
           'uitableview', 'unit-testing', 'symfony', 'powershell', 'class', 'loops',
            'amazon-web-services', 'csv', 'azure', 'validation', 'google-chrome',
             'sql-server-2008', 'sockets', 'sorting', 'date', 'tsql', 'xaml', 'selenium', 'wcf',
              'android-layout', 'email', 'jsp', 'visual-studio-2010', 'spring-mvc', 'http',
               'typescript', 'listview', 'numpy', 'security', 'oop', 'android-studio', 'opencv',
                'parsing', 'firebase', 'user-interface', 'c++11', 'datetime', 'asp.net-mvc-4',
                 'actionscript-3', 'delphi', 'google-app-engine', 'batch-file', 'ubuntu', 'express',
                  'templates', 'asp.net-mvc-3', 'pointers', 'debugging', 'object', 'session',
                   'variables', 'jquery-ui', 'dictionary', 'unix', 'cocoa', 'ms-access', 'magento',
                    'hadoop', 'internet-explorer', 'for-loop', 'haskell', 'apache-spark',
                     'android-fragments', 'ruby-on-rails-4', 'tomcat', 'pdf', 'authentication',
                      'flash', 'if-statement', 'ipad', 'cocoa-touch', 'ssl', 'docker', 'jsf', 'jpa',
                       'generics', 'url', 'animation', 'firefox', 'facebook-graph-api', 'redirect',
                        'winapi', 'curl', 'spring-boot', 'inheritance', 'asynchronous', 'unity3d',
                         'elasticsearch', 'exception', 'testing', 'opengl', 'events', 'caching',
                          'xslt', 'mod-rewrite', 'servlets', 'nginx', 'dataframe', 'post',
                           'cakephp', 'math', 'dom', 'iis', 'select', 'button', 'd3.js',
                            'join', 'xamarin', 'search']


def get_relevant_quest(org_ques, quest_dict):

  



def remove_spam(text):


  text = text.replace('&#39;', ' ')
  text = text.replace('&quot', ' ')

  new = ''

  for e in text:
    if e.isalnum() or e == ' ':
      new += e

    else:
      new += ' '

  return new


def get_top_answer(question):

  words = question.split(' ')
  kywds = [w for w in all_tags if w in words] 

  url = 'https://api.stackexchange.com/2.2/search/advanced?order=desc&site=stackoverflow&accepted=False&filter=!9YdnSJ*_T&sort=votes&q='

  for w in kywds:

    tag = '[' + w + '] OR '
    url += tag

  url = url[: -4]

  print(kywds)
  r = requests.get(url)

  questions_json = []
  for ques in r.json()['items']:

    title = remove_spam(ques['title'])
    body = remove_spam(ques['body_markdown'])

    current_ques = {'title': title, 'id': ques['question_id'], 'body': body}
    questions_json.append(current_ques)


  pprint(questions_json[0])


get_top_answer("I rock at python and java ...")



# r = requests.get('https://api.stackexchange.com/2.2/questions/48520049/answers?order=desc&sort=votes&site=stackoverflow&filter=withbody')
# pprint(r.json()['items'])  