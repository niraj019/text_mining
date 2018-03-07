

import nltk, re, pickle,sys,os
from nltk import pos_tag
from Dialog import Dialog

     #text = comb_line_sent(my_corpus.sents(f1))
     #print_text(text[0],text[1])
     #print_text(text[0])
def print_text(text, with_labels = None,save=False):
    if save:
        file = open('temp_output.txt','w')
    if with_labels != None:
        for i,sent in enumerate(text):
            line = str(i) + ".\t- "+ str(sent) + "\t -" + with_labels[i]
            print(line)
            if save:
                file.write(line + "\n")
    else:
        for i,sent in enumerate(text):
            line = str(i) + ".\t- " + str(sent)
            print(line)
            if save:
                file.write(line + "\n")

def contains_punct(sent):
    acronyms = set(['dr.','mr.','mrs.','prof.','u.s..', 'u.s', 'st.'])
    punc_set = set(['.','!','?'])
    punct = False
    indices = [word_index for word_index, word in enumerate(sent) if word in punc_set] #Find all indices of a '.'
    for index in indices:
        punc_occ = sent[index]
        if not(punc_occ.lower() in acronyms):
              punct = True
    return punct

def is_end(full_sent):
    pattern = re.compile('^THE?\s?END$|^BLACK\sOUT$') #Use regular expression as END have a proper amount of instances that is nested in figures, such as "Vendor".
    this_is_end = False
    if pattern.match(full_sent):
        this_is_end =True
    return this_is_end

def is_transit(full_sent):
    trans_set = set(['FADE', 'DISSOLVE']) #Detect FADE IN, FADE OUT, FADE TO etc and same for dissolve.
    is_trans = False
    for trans_word in trans_set:
        if trans_word in full_sent:
            is_trans = True
    return is_trans

def is_figure(full_sent,next_sent,prev_label, has_punc):
    #not ('-' in full_sent) and ( not (has_punc) or ('.' in full_sent and figure_pattern.match(full_sent)))
    figure_pattern = re.compile('^.+\(.+\)$')  # For finding figures through NAMEFIGURE ( ON T.V. ) or NAMEFIGURE (CONT'D) or NAMEFIGURE (V.O.) voice over and NAMEFIGURE (O.S.) (off-screen) etc
    not_figure_symbols = set(['-', '!'])
    non_fig_prop_found = False
    result = False
    for symbol in not_figure_symbols:
        if symbol in full_sent:
            non_fig_prop_found = True
        elif (next_sent != None  and symbol in " ".join(next_sent)) and (prev_label != "FIGURE"): #For cases of capital letters in current sentence but is missing ! next sentence (is split) and actually speech
            non_fig_prop_found = True

    if (not(non_fig_prop_found)) and ((not(has_punc)) or ('.' in full_sent and figure_pattern.match(full_sent))): #Making sure not an sentence in capital with ! in current sentence, has no punctuation or if it does is have this form example FIGURE ( ON T.V )
        result = True
    return result

def comb_line_sent(text):
    newtext = []
    labellist = []
    sent_index = 0
    size = len(text)
    found_start = False
    found_end = False

    while (sent_index < size) and not(found_end):
         newsent = []
         punc_found = False

         while not(punc_found) and (sent_index < size):
              curr_sent = text[sent_index]
              if sent_index+1 != size:
                  next_sent = text[sent_index + 1]
              else:
                  next_sent = None
              last_label = None
              full_sent = " ".join(curr_sent)
              action_pattern = re.compile('^\(.+\)$') #For finding actions through ( .. )
              is_capital = full_sent.isupper()
              has_punc = contains_punct(curr_sent)
              is_fig = is_figure(full_sent,next_sent,last_label,has_punc) #Detecting figures, consist of capitals, but transitions and certain dialogs can have capitals to
                                                                                                                     #So figures usually have no punctutation or when it does its NAME ( SOMETHING ) with sometimes a '.' but never !. Places are also indicated with - in name usually
              if is_capital and is_transit(full_sent): #Skip over transition, do add SPEECH before that if it was not already added.
                  found_start = True
                  if len(newsent):
                      newtext.append(newsent)
                      labellist.append("SPEECH")
                      last_label = "SPEECH"
                  sent_index +=1
                  break
              elif is_capital and is_fig:  #Capitals letters are figures or a narrator of movie. (Treat as figures) With exception of transition FADE and DISSOLVE
                 punc_found = found_start = True
                 if is_end(full_sent):  #Check if it is the end
                     found_end = True
                     break
                 if len(newsent):
                     newtext.append(newsent)   #If not punc was found before this capital figure, than there is still text (sentence) in newsent or curr_sent has capital followed by ! in next sentence
                     labellist.append("SPEECH")
                     last_label = "SPEECH"
                 newtext.append(curr_sent)  #Add the figure as a seperate sentence
                 labellist.append("FIGURE")
                 last_label = "FIGURE"
              elif found_start and action_pattern.match(full_sent):  #Check if it is a action
                  if len(newsent):
                      newtext.append(newsent)  #Same principle as stated for figures, if there was text in newsent, add them seperately to newtext.
                      labellist.append("SPEECH")
                      last_label = "SPEECH"
                  newtext.append(curr_sent)
                  labellist.append("ACTION")
                  last_label = "ACTION"
              elif has_punc and found_start: #If punctation is found, the whole sentence is combined and can be appended
                 punc_found = True
                 newsent += curr_sent
                 while ( (sent_index + 1 < size) and (len(text[sent_index + 1]) == 1) and contains_punct(text[sent_index + 1])): #While multiple punctations lke !! or ?? are seperated, make sure they are combined and keep checking
                     next_sent = text[sent_index + 1]
                     newsent += next_sent
                     sent_index += 1
                 newtext.append(newsent)
                 labellist.append("SPEECH")
                 last_label = "SPEECH"
              elif found_start:       #Combine sentences that are spread over multiple lines in text file and that was seperated by NLTK tokenizer.
                 newsent += curr_sent
              sent_index += 1

    return (newtext,labellist)

def sent_less_than(dialogs,sent_minimal):
    list = []
    for dialog in dialogs:
        if (dialog.amount_sent < sent_minimal):
            tuple = (dialog.genre,dialog.movie_name,dialog.amount_sent)
            list.append(tuple)
    return list

def move_files(list_to_remove):

    for (genre_list,movie_name,amount_sent) in list_to_remove:
        for genre in genre_list:

            current_path = "./dialogs>500/" + genre + "/" + movie_name + ".txt"

            if not os.path.exists("./moved_files"):
                os.makedirs("./moved_files")
            new_path = "./moved_files/" + genre + "-" + movie_name + ".txt"
            os.rename(current_path,new_path)

def main():
    my_corpus = nltk.corpus.PlaintextCorpusReader('./dialogs>500', '.*\.txt')
    listfiles = my_corpus.fileids()  # All files, with directory (genre) at the start)
    f1 = listfiles[0]
    #print(f1)
    dialogs = []
    for direc_file in listfiles:
         print(direc_file)
         duplicate_dialog = False

         split_index = direc_file.find('/')
         ext_index = direc_file[split_index:].find('.')
         end_name = split_index + ext_index
         genre = direc_file[:split_index]
         movie_name = direc_file[split_index+1:end_name]

         for dialog in dialogs:  #If already parsed, but has another genre, add genre to the list in Dialog object
             if dialog.check_name(movie_name):
                 duplicate_dialog = True
                 dialog.add_genre(genre)
                 break

         if not(duplicate_dialog):
             text = comb_line_sent(my_corpus.sents(direc_file))
             d = Dialog(movie_name, genre, text[0], text[1])
             dialogs.append(d)
             if len(text[0]) != len(text[1]):
                 print("Error, Len of sentences do not match len of labels")
                 print("Len of text %d and len of labels is %d", len(text[0]), len(text[1]))
                 sys.exit(1)

    pickle.dump(dialogs, open("adjusted_dialogs.p", "wb"))
         #print_sent(text)
    #text = pickle.load(open("all_dialogs.p", "rb"))
    #print_text(text[0],text[1])
    #d1 = Dialog('test','test',text[0],text[1])
    print("Movie name {}\nGenre {}\nAmount sent {}\nAmount action {}\nAmount figures {}\nFigures is {}".format(d.movie_name, d.genre, d.amount_sent,d.amount_action,d.amount_figures,str(d.figures_set)))


if __name__== "__main__":
    main()
     
'''
Notes
#Capitals letters are figures or a narrator of movie. (Treat as figures) With exception of transition FADE and DISSolve
#Consider actions that are in script notated like (throws) or (to Nick) speaking. (Treat as actions). 
#Rest are sentences of speech (Treat as speech)
#Consider when start of dialog, probably when first figure is encountered, most universal solution. Some file might take a few sentences that are not of script, but info about script
#End of dialog. Capitals with words: (THE) END, BLACK OUT otherwise end of file reach for other exceptions or not noting THE END.
#Delete files with only movie figures and no text (Such as action/wildhogs_dialog.txt and more)

To do for parse:
Delete files with only movie figures and not speech sentences, use of label. And maybe exclude some genres that does not contain many scripts and has class inbalance.
   Files with less than 300 sentences are 101 dialogs files. 
   Less than 500 sentenes are 115 dialogs files.
   Less than 1000 sentences are 186 dialogs files.
Pos tag dialogs
'''