

# tags = requests.get('https://api.stackexchange.com/2.2/tags?page=1&pagesize=100&order=desc&sort=popular&site=stackoverflow')
# items = tags.json()['items']
# all_tags_1 = [t['name'] for t in items] 

# tags = requests.get('https://api.stackexchange.com/2.2/tags?page=2&pagesize=100&order=desc&sort=popular&site=stackoverflow')
# items = tags.json()['items']
# all_tags_2 = [t['name'] for t in items]

# all_tags = all_tags_1 + all_tags_2 
# print(all_tags)


chars_to_skip = {',', '\'', '"', ':', '-', '?', '!', '&', '+', '#', '@', '/',
          '\\', '(', ')', '{', '}', '%', '^', '*', '_'}
stop_words = {'a','in', 's', 'do', 'that', 'between', 'most', 'who', 'their',
'now', 'be', 'which', 'ourselves', 'my', 'some', 'of', 'the', 'to', 'hasn',
'about', 'was', 'before', 'its', 'but', 'with', 'have', 'on', 'own', 'ma',
'them', 'doesn', 'mustn', 'a', 'same', 'yourself', 'y', 'is', 'for', 'where',
'aren', 'had', 'didn', 'o', 'this', 'himself', 'in', 'further', 'only', 'against',
't', 'each', 'as', 'i', 'just', 'if', 'out', 'were', 'from', 'has', 'again',
 'through', 'we', 'how', 'me', 'so', 'does', 'off', 'yourselves', 'you', 'below',
  'wasn', 'been', 'because', 'any', 'am', 'will', 're', 'ain', 'during', 'or',
   'than', 'your', 'when', 'these', 'wouldn', 'll', 'haven', 'itself', 'more',
  'she', 'while', 'yours', 'by', 'both', 'couldn', 'his', 'at', 'down', 've',
   'mightn', 'and', 'after', 'then', 'theirs', 'it', 'such', 'our', 'those',
    'don', 'what', 'he', 'themselves', 'd', 'whom', 'him', 'above', 'ours',
     'once', 'can', 'weren', 'under', 'not', 'there', 'here', 'shan', 'why',
    'being', 'they', 'm', 'won', 'into', 'over', 'up', 'needn', 'few', 'isn',
     'are', 'shouldn', 'too', 'hadn', 'myself', 'did', 'her', 'having', 'very',
      'herself', 'doing', 'hers', 'should', 'no', 'all', 'nor', 'an', 'other',
       'until', 'also'}

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

import requests
from pprint import pprint
from textblob import Word
from textblob import TextBlob
from textblob.wordnet import Synset


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


def get_relevant_quest(org_ques, all_quest_dicts):
  '''
  Args:
    org_quest : String
    all_quest_dicts : List of dictionaries holding all slightly relevant questions

  Returns:
    dictionary with most relevant question

  '''

  org_ques = remove_spam(org_ques).split(' ')
  org_ques = [w for w in org_ques if w not in stop_words]

  for org_word in org_ques:

    for quest_dict in all_quest_dicts:

      ctr = 0

      for quest_kwd in quest_dict['body_kwds']:

        curr_max = 0
        org_syns = Word(org_word).synsets
        quest_syns = Word(quest_kwd).synsets

        if len(org_syns) == 0 or len(quest_syns) == 0:
          continue

        for org_syn in org_syns:

          for quest_syn in quest_syns:

            pathsim = org_syn.path_similarity(quest_syn)

                if pathsim is not None and pathsim > curr_max:
                  curr_max = pathsim


        if curr_max != 0:
          ctr += 1
          quest_dict['pts'] += curr_max



  max_pts = 0
  index_most_relevant = -1
  for i, quest_dict in enumerate(all_quest_dicts):

    if quest_dict['pts'] > max_pts:
      max_pts = quest_dict['pts']
      index_most_relevant = i


  return all_quest_dicts[index_most_relevant]






def get_all_ques(question):

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

    body_kwds = body.split(' ')
    body_kwds = [w for w in body_kwds if w not in stop_words]


    current_ques = {'title': title, 'id': ques['question_id'],
     'body': body, 'body_kwds': body_kwds, 'pts': 0}
    questions_json.append(current_ques)


  return questions_json



def get_top_answer(ques_id):

  r = requests.get('https://api.stackexchange.com/2.2/questions/48520049/answers?order=desc&sort=votes&site=stackoverflow&filter=withbody')
  ans = r.json()['items'][0]
  pprint(ans)
  return ans




def run(org_question):

  all_ques = get_all_ques(org_question)

  relevant_ques = get_relevant_quest(org_question, all_ques)

  ques_id = relevant_ques['id']

  top_answer = get_top_answer(ques_id)


  return relevant_ques, top_answer