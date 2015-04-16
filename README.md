# jpod2anki
A simple script for creating Anki flashcards from a Jpod lesson page

# Usage

Navigate to the desired lesson page and make sure you have expanded the Lesson Materials > Vocabulary tab (otherwise
the vocab won't show up in the downloaded page). Download the page via Chrome using the "Webpage, Complete" option.

Run jpod2anki using:

```bash
python parse.py path/to/page.html
```

Inside of Anki click "Import File", select "Allow HTML in fields", and browse to the ankideck file created by jpod2anki.
You can verify the successful import by using the "Browse" screen, selecting the appropriate deck, and searching for the tag
given by jpod2anki, e.g. "tag:121__Going_Up!". 

Finally, you'll need to transfer the audio file from the `ankideck.media` directory created by jpod2anki to the 
`~/Documents/Anki/User\ 1/collection.media` directory that Anki uses. 
