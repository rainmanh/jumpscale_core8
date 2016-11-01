<!-- toc -->
## j.tools.console

- /opt/jumpscale8/lib/JumpScale/tools/console/Console.py
- Properties
    - width
    - logger
    - indent

### Methods

class which groups functionality to print to a console
self.width=120
self.indent=0 #current indentation of messages send to console
self.reformat=False #if True will make sure message fits nicely on screen

#### askArrayRow(*array, header=True, descr='', returncol*) 

#### askChoice(*choicearray, descr='', sort=True, maxchoice=60, height=40, autocomplete*) 

```
@param choicearray is list or dict, when dict key needs to be the object to return,
       the value of the dics is what needs to be returned, the key is the str
    representation

```

#### askChoiceMultiple(*choicearray, descr, sort=True*) 

#### askInteger(*question, defaultValue, minValue, maxValue, retry=-1, validate*) 

```
Get an integer response on asked question

@param question: Question need to get response on
@param defaultparam: default response on the question if response not passed
@param minValue: minimum accepted value for that integer
@param maxValue: maximum accepted value for that integer
@param retry: int counter to retry ask for respone on the question
@param validate: Function to validate provided value

@return: integer representing the response on the question

```

#### askIntegers(*question, invalid_message='invalid input please try again.', min, max*) 

```
Ask the user for multiple integers

@param question: question that will be echoed before the user needs to input integers
@type question: string
@param invalid_message: message that will be echoed when the user inputs a faulty value
@type invalid_message: string
@param min: optional minimal value for input values, all returned values will be at least
    min
@type min: number or None
@param max: optional maximal value for input values, all returned values will be at least
    max
@type max: number of None
@return: the input numbers
@rtype: list<number>

```

#### askMultiline(*question, escapeString='.'*) 

```
Ask the user a question that needs a multi-line answer.

@param question: The question that should be asked to the user
@type question: string
@param escapeString: Optional custom escape string that is used by the user to indicate
    input has ended.
@type escapeString: string
@return: string multi-line reply by the user, always ending with a newline

```

#### askPassword(*question, confirm=True, regex, retry=-1, validate*) 

```
Present a password input question to the user

@param question: Password prompt message
@param confirm: Ask to confirm the password
@type confirm: bool
@param regex: Regex to match in the response
@param retry: Integer counter to retry ask for respone on the question
@param validate: Function to validate provided value

@returns: Password provided by the user
@rtype: string

```

#### askString(*question, defaultparam='', regex, retry=-1, validate*) 

```
Get a string response on a question

@param question: Question to respond to
@param defaultparam: Default response on the question if response not passed
@param regex: Regex to match in the response
@param retry: Integer counter to retry ask for respone on the question
@param validate: Function to validate provided value

@returns: Response provided by the user
@rtype: string

```

#### askYesNo(*message=''*) 

```
Display a yes/no question and loop until a valid answer is entered

@param message: Question message
@type message: string

@return: Positive or negative answer
@rtype: bool

```

#### cls() 

```
clear screen

```

#### echo(*msg, indent, withStar, prefix='', log, lf=True*) 

```
Display some text to the end-user, use this method instead of print
@param indent std, will use indent from console object (same for all), this param allows
    to overrule
        will only work when j.tools.console.reformat==True

```

#### echoDict(*dictionary, withStar, indent*) 

#### echoListItem(*msg*) 

```
Echo a list item
@param msg: Message to display

```

#### echoListItems(*messages, sort*) 

```
Echo a sequence (iterator, generator, list, set) as list items

@param messages: messages that need to be written to the console as list items
@type messages: iterable
@param sort: sort the messages before echoing them
@type sort: bool
@param loglevel: Log level
@type loglevel: number

```

#### echoListWithPrefix(*messages, prefix*) 

```
print messages

```

#### echoWithPrefix(*message, prefix, withStar, indent*) 

```
print a message which is formatted with a prefix

```

#### enableOutput() 

#### formatMessage(*message, prefix='', withStar, indent, width, removeemptylines=True*) 

```
Reformat the message to display to the user and calculate length
@param withStar means put * in front of message
@returns: Length of last line and message to display
@rtype: tuple<number, string>

```

#### getOutput() 

#### hideOutput() 

#### printOutput() 

#### rawInputPerChar(*callback, params*) 

```
when typing, char per char will be returned

```

#### showArray(*array, header=True*) 

#### transformDictToMessage(*dictionary, withStar, indent*) 

