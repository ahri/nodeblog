# coding: UTF-8
from lxml.builder import E, ET
from copy import copy
import urllib
from functools import wraps
from werkzeug.wrappers import BaseResponse

def CLASSES(*args):
    return {'class': ' '.join(args)}

SITE_TITLE = 'ahri.net'
SITE_URL = 'ahri.net'
AUTHOR_NAME = 'Adam Piper'
AUTHOR_EMAIL = 'adam@ahri.net'
YEAR = 2011

HTML = E.html(
    E.head(
        E.title(SITE_TITLE),
        E.meta(**{'http-equiv': 'Content-Type', 'content': 'text/html; charset=UTF-8'})
    ),
    E.body(
        E.div(
            E.div(
                E.a(SITE_TITLE, href=SITE_URL),
                id='site-title',
            ),
            E.div(id='links'),
            id='header',
        ),
        E.h1('', id='page-title'),
        E.div(id='content'),
        E.div(
            E.hr(),
            E.p(
                u'Copyright © ',
                E.a(
                    AUTHOR_NAME,
                    href='mailto:' + AUTHOR_EMAIL,
                ),
                ' ' + str(YEAR),
            ),
            id='footer',
        ),
    ),
)

HEAD = HTML.xpath("/html/head")[0]
BODY = HTML.xpath("/html/body")[0]
HEADER = HTML.xpath("//*[@id='header']")[0]

def stylesheet(url):
    return E.link(rel='stylesheet', type='text/css', media='screen', href=url)

def javascript(url):
    return E.script('', type='text/javascript', src=url)

def embed_nodes(title=None, css=[], js=[], removals=[]):
    """
    Decorator to embed nodes inside the HTML node tree
    Pass URLs for css/js to have them added appropriately
    Pass xpaths to be removed
    """

    def magic(f):
        @wraps(f)
        def call(*args, **kwargs):
            html = copy(HTML)
            content = html.xpath("//html/body/*[@id='content']")[0]
            res = f(*args, **kwargs)

            if type(res) is BaseResponse:
                return res

            for item in res:
                content.append(item)

            if title is not None:
                html.xpath("//title")[0].text += (' - ' + title)
                html.xpath("//*[@id='page-title']")[0].text = '> %s' % title

            HEAD = html.xpath("/html/head")[0]
            BODY = html.xpath("/html/body")[0]

            for url in css:
                HEAD.append(stylesheet(url))

            for url in js:
                BODY.append(javascript(url))

            for remove in removals:
                node = html.xpath(remove)[0]
                node.getparent().remove(node)

            # make sure all fields take UTF-8
            for element in html.xpath("//input | //textarea"):
                element.attrib['accept-charset'] = 'UTF-8'

            return '<!DOCTYPE HTML>\n%s' % ET.tostring(html, pretty_print=True)
        return call
    return magic

# Add css
for url in ['http://static.ahri.net/css/base.css',
           ]:
    HEAD.append(stylesheet(url))

# Add google fonts
for font in ['Crimson Text', 'Droid Sans Mono', 'Lobster']:
    HEAD.append(stylesheet('http://fonts.googleapis.com/css?family=%s' % urllib.quote_plus(font)))

# Add some links
for name, url in [('Blog', 'http://www.ahri.net'),
                  ('Photos', 'http://photos.ahri.net'),
                  ('Code Repos', 'http://github.com/ahri'),
                  ('Regex Guide', '/regex'),
                  ('Apostrophe Guide', '/apostrophes'),
                  ('Music', '/music'),
                  ('Login', '/login'),
                 ]:
     HEADER.xpath("//div[@id='links']")[0].append(E.a('[%s]' % name, href=url))

POST = E.div(
    E.div(
        E.h4(CLASSES('text')),
        CLASSES('title'),
    ),
    E.div(CLASSES('datetime')),
    E.div(CLASSES('content')),
    CLASSES('post'),
)

SPACER = E.div(
    E.hr(),
    CLASSES('spacer'),
)

CV = E.cv(
    E.date("2011-07-05"),

    E.person("Adam Piper",
             dob="18 January 1983",
             address="Apt. 320, 5 Ludgate Hill, Manchester, M4 4TJ",
             phone="07989572270",
             email="adam@ahri.net"),

    E.goal("Senior developer involving a high level of responsibility and team leadership duties"),

    E.profile(
        E.item("13 years' experience in software development, with experiencerience in all aspects of the project life-cycle."),
        E.item("Over 3 years' exposure to the Energy and Utilities, Oil and Gas industry."),
        E.item("Well versed in agile methodologies including Test-Driven Development, scrum, pair programming."),
        E.item("Extensive technical skill set with an advanced understanding of OO concepts and expertise in a number of development tools, including .NET, Java, SQL and many open source tools such as vim, git, svn."),
        E.item("Excellent communication skills with experience of working closely with clients and third party contractors."),
        E.item("Confident in leading teams to development, manage and deliver innovative business solutions in a timely manner with an emphasis on quality and efficiency."),
        E.item("Highly motivated and detail-oriented individual with excellent analytical and problem solving skills. Performs effectively under pressure and uses initiative to develop efficiency enhancing tools beyond specification to compliment projects."),
    ),

    E.skillset(
        E.expert(
            E.item("Python"),
            E.item("PHP"),
            E.item("HTML"),
            E.item("SQL"),
            E.item("Linux"),
            E.item("Shell Scripting (UNIX)"),
            E.item("Data Modelling (UML)"),
            E.item("Apache Web Server"),
        ),
        E.experienced(
            E.item("C"),
            E.item("C#"),
            E.item("Java"),
            E.item("Ada"),
            E.item("OpenRoad (4GL)"),
            E.item("Ingres (ServerSQL)"),
            E.item("Javascript"),
            E.item("MS Office"),
        ),
        E.exposure(
            E.item("Perl"),
            E.item("Visio"),
            E.item("Microsoft SQL Server"),
            E.item("Visual Studio"),
            E.item("Ruby"),
            E.item("Scheme (Lisp)"),
            E.item("Haskell"),
        ),
    ),

    E.career(
        E.role("Web/Embedded Developer", begin="February 1998", end="August 2006", company="Redileads Anglesey Ltd."),
        E.role("Freelance Web Developer", begin="October 2006", end="January 2009", company="SevenPointSix.com"),
        E.role("Senior Analyst/Developer", begin="July 2007", end="Present", company="Logica"),
    ),

    E.details(
        E.job(),
    ),

    E.education(),

    E.activities(),

    E.skills()
)
