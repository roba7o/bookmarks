from pprint import pprint


class BarkDog:
    def bark(self):
        print("Woof")


rex = BarkDog()


# bark() is syntactic sugar -> binds instance automatiically
rex.bark()  # Doesnt just grab function -> goes thru descriptor protocol
# accessing it through an instance triggers -> returning a bound method
BarkDog.bark.__get__(rex, BarkDog)()

# This skips that and passes instnace manually.
BarkDog.bark(rex)


class GreetDog:
    growl_noise = "Grrrr"
    # Doesnt work! Python uses LEGB scoping. CLASS BODY NOT IN CHAIN!!!!
    # its never in the E-scope for methods inside it
    # lives in GreetDog.__dict__

    def set_name(self, name):
        # setting an attribute at the instance level
        # can be accessed via child via instance.name
        self.name = name

    def grabbing_desc_level(self):
        for key, val in self.__dict__.items():
            print(f"Instance attr: {key} = {val}")

        # To access class-level attributes
        print(f"Class attribute growl_noise: {self.growl_noise}")  # Access via self
        print(f"Class attribute growl_noise via class: {GreetDog.growl_noise}")

    def greet(self):
        # or can be acccessed from a class-method
        print(f"hi my name is {self.name}!")

    def angry(self):
        # print(growl_noise) LEGB ERROR!
        # local? no. enclosing? no. global no. builtin? no. -> NameError!

        # Note: class scope is invisible at run time
        # needs attribute look-up via dot operator (.)
        print(self.growl_noise)

    def angry_greet(self):
        print(f"{self.growl_noise} my name is {self.name}")

    def instance_dict_printout(self):
        pprint(self.__dict__)

    # Class level methods
    @classmethod
    def all_dict_values(cls):
        pprint(cls.__dict__)

    @classmethod
    def defined_dicts_only(cls):
        for key, val in cls.__dict__.items():
            if not key.startswith("__"):
                print(f"{key:20} {val}")

    @staticmethod
    def all_dict_values_static():
        pprint(GreetDog.__dict__)


max = GreetDog()
max.set_name("Max")


GreetDog.greet(max)
