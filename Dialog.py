class Dialog:

    def __init__(self, movie_name, genre, list_of_sent, labels):
        self.movie_name = movie_name
        self.genre = [genre]
        self.full_dialog = list_of_sent
        self.labels = labels
        self.calc_amount_each_label(list_of_sent,labels)

    def calc_amount_each_label(self, list_of_sent, labels):
        self.amount_sent = 0
        self.amount_action = 0
        self.amount_figures = 0
        self.figures_set = set()

        for i,label in enumerate(labels):
            figure = " ".join(list_of_sent[i])
            if '(' and ')' in figure: #Only taking NAMEFIGURE and not NAMEFIGURE ( ON T.V. ) or NAMEFIGURE (CONT'D) or NAMEFIGURE (V.O.) or NAMEFIGURE (O.S.) etc.
                end_name_index = figure.find("(")
                figure = figure[:end_name_index]

            if label == "SPEECH":
                self.amount_sent += 1
            elif label == "ACTION":
                self.amount_action += 1
            elif label == "FIGURE" and not(figure in self.figures_set):
                self.amount_figures += 1
                self.figures_set.add(figure)

    def check_name(self,movie_name):
        result = False
        if self.movie_name == movie_name:
            result = True
        return result

    def add_genre(self,genre):
        self.genre.append(genre)
        return self.genre

    def get_speech(self):
        sent_list = []
        for i,sent in enumerate(self.full_dialog):
            if self.labels[i] == "SPEECH":
                sent_list.append(sent)
        return sent_list

    def get_action(self):
        action_list = []
        for i,sent in enumerate(self.full_dialog):
            if self.labels[i] == "ACTION":
                action_list.append(sent)
        return action_list

    def get_figures(self):
        non_unique_figures_list = []
        for i,sent in enumerate(self.full_dialog):
            if self.labels[i] == "FIGURE":
                non_unique_figures_list.append(sent)
        return non_unique_figures_list

