""" The CoqResponse class holds all the details returned by coqtop. """

class CoqResponse:

    def __init__(self, rep):
        self.noResponse = False
        if not rep is None:
            if rep.get('val') == 'good':
                self.success = True
                infos = rep.find('string')
                if not infos is None:
                    self.infos = infos.text
                else:
                    self.infos = ""
            else:
                self.success = False
                self.error = str(rep.text)
        else:
            self.noResponse = True

    def get(self):
        """ Retrieve the reponse details in this format :
            (error [boolean], message [string]). """
        if self.noResponse:
            return None
        if self.success:
            return (True, self.infos)
        else:
            return (False, self.error)
