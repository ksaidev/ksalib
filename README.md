# KSA library

A library enabling developers to easily build simple and complicated programs for use in KSA


Authorization
-------------

### Authorization expires after a few dozen minutes. Refresh Login Every few minutes to avoid errors.

This library supports lms, student site, and gaonnuri. For more support, create an issue.

To Authorize

    user=Auth()
    user.gaonnuri_auth('id','pwd')
    user.student_auth('id','pwd')
    user.lms_auth('id','pwd')

Post Class
-------------
The Post class is a class that represents an individual gaonnuri post. In takes an authorization class as an input. You can use it in the following way.

    post=Post(user, link of post)

There are many attributes of a `Post` class

    post.title
    post.time
    post.author
    post.views

You can print the article in two forms in the following way. The `html` form, and `markdown` ( just text ) form.

    post.html()
    post.text()

both return a string.

Sugang Class
-------------
`Sugang` class is a class that represents your 수강상태. It takes an authorization class as an input. You can use it in the following way.

    sugang=Sugang(user)

It has three methods.

`sugang.table` returns your classes as a list

`sugang.timetable` returns your classes as a list

`sugang.info` returns information about you (ex : your grade, number, et cetra)


Exploit Class
-------------
`Exploit` class is a class that enables users to do actions that are supposed to be blocked. It takes an authorization class as an input. You can use it in the following way

    exploit=Exploit(user)

It currently has three methods.

`exploit.outing()` 외출 외박 신청이 되있을때 외출 체크를 할 수 있게 해줌


Methods
-------------
### Acessing the Board

There are two main ways to access a board. One returns a list of `Post` classes, and the other returns only basic informaion about each post.


#### 1. To get a list of `Post` classes, use

    get_gaonnuri_board_post(user,board="board name")


#### 2. To access the basic information about a post, use

    get_gaonnuri_board(user,board="board name")

The `"board name"` has to be one on gaonnuri, for example `"board_notice"` or `"board_SuQZ12"`.
This will return each notice in the following json format.

      {
      'no':no,
      'title':title,
      'link':link,
      'author':author,
      'time':time,
      'views':views
      }

All posts will be appended to a list.

To access the one-line post, use

    get_gaonnuri_oneline(user)

This method will return a list of all gaonnuri one-line posts

### Acessing 상점, 벌점

To access 상점, 벌점, use the following method.

    get_student_points(user)

The method takes an authorization class as an input. It returns the 상점, 벌점 as a dictionary.
