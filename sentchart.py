import webapp2
import json
import jinja2
import os
from google.appengine.api import urlfetch
import logging
import re

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainPage(webapp2.RequestHandler):
     def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(""))
        application = webapp2.WSGIApplication([
            ('/', MainPage),
        ], debug=True)

class testpage(webapp2.RequestHandler):
     def get(self):
        self.response.write('<html><body>You wrote:<pre>')
        self.response.write(self.request.get('name'))
        self.response.write('</pre></body></html>')

class gaembed(webapp2.RequestHandler):
     def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        template = JINJA_ENVIRONMENT.get_template('gaembed.html')
        self.response.write(template.render(""))
        application = webapp2.WSGIApplication([
            ('/', MainPage),
        ], debug=True)

class charts(webapp2.RequestHandler):

    def get(self):
        ## get inputs from url
        urlfetch.set_default_fetch_deadline(45)
        posts=self.request.get('posts')
        alc_key=self.request.get('alc_key')
        api_key=self.request.get('api_key')
        license_id=self.request.get('license_id')
        dummy=self.request.get('dummy')
        # call Percolate + Alchemy Service
        url='http://percolate-post-analyzer.appspot.com/sentiment?api_key='+api_key+'&posts='+posts+'&license_id='+license_id+'&dummy='+dummy+'&alc_key='+alc_key
        percreq=urlfetch.fetch(url)
        #log response
        logging.debug(percreq.content)
        # translate JSON response - should add logic for bad response here.
        percposts= json.loads(percreq.content)

        template = JINJA_ENVIRONMENT.get_template('chart.html')
        # data=[
        #   [ (2015, 0, 25),      12],
        #   [ (2015, 0, 26),      5.5],
        #   [ (2015, 0, 27),     14],
        #   [ (2015, 0, 28),      5],
        #   [ (2015, 0, 30),      3.5],
        #   [ (2015, 0, 31),    7]
        # ]
        data=[]
        for post in percposts['data']:
            date=(int(post['published_at'][0:4]),int(post['published_at'][5:7])-1,int(post['published_at'][8:10]))
            try:
                data.append([date,float(post['sentiment']['score']),re.sub(r'[^\w]', ' ',  post['post'])])
            except:
                data.append([date,0,re.sub(r'[^\w]', ' ',  post['post'])])
        #template_values={'chartdata':json.dumps(data)}
        template_values={'chartdata':data}
        #self.response.headers['Content-Type'] = 'text/html'
        logging.debug(template_values)
        self.response.write(template.render(template_values))


application = webapp2.WSGIApplication([
    ('/', MainPage),
    (r'/charts', charts),
    (r'/test', testpage),
    (r'/gaembed', gaembed),
], debug=True)