from datetime import datetime
from json import load
from pathlib import Path
from random import choice, randint
from typing import List

__all__: List[str] = ['Report']

CWD: str = str(Path(__file__).parents[0]).replace('\\', '/')
PATH_DEFAULT_INVENTORY: str = CWD + '/_default_inventory.json'
PATH_DEFAULT_TEMPLATE: str = CWD + '/_default_template.txt'


class Report:

    def __init__(self, inventory: dict = {}, entries: int = 5) -> None:
        """Initializes a new :class:`Report` object.

        Parameters
        -----------
        inventory: :class:`dict`
            Key: Value pairs that represent Cheap, Medium and Expensive items
            that may be found in a Grocery store. There are (3) Keys and they
            must be named '$', '$$' and '$$$'. The values are lists of items.
        entries: :class:`int`
            The number of random entries to generate for the report.
            Default is :int:`5`.
        """

        if (inventory == {}):
            with open(PATH_DEFAULT_INVENTORY, 'r') as fp:
                inventory = load(fp)

        self.inventory: dict = {
            '$': inventory.pop('$', ['_Default$Item']),
            '$$': inventory.pop('$$', ['_Default$$Item']),
            '$$$': inventory.pop('$$$', ['_Default$$$Item'])
        }
        self.entries: int = entries
        self._auto_align: bool = True
        self._item_fmt: str = '{item} = {price}'

        with open(PATH_DEFAULT_TEMPLATE, 'r') as f:
            self._template: List[str] = [x.strip() for x in f.readlines()]

    @property
    def template(self) -> List[str]:
        """:class:`list` Determines how to format the final output in
        :meth:`generate_report`.
        """

        return self._template

    @template.setter
    def template(self, value: List[str]) -> None:

        self._template = value

        return None

    @property
    def item_fmt(self) -> str:
        """:class:`str` Determines how to format the '{item} and {price}'
        when generating entries in :meth:`generate_report`.
        """

        return self._item_fmt

    @item_fmt.setter
    def item_fmt(self, value: str) -> None:
        """Change the way the '{item} = {price}' is displayed when generating
        a new report.

        Parameters
        -----------
        value: :class:`str`
            The new format to override the existing with.

        NOTE
        -----
        There are keywords the program searches for when generating entries.
        These are required when writing a custom format: '{item}', '{price}'.

        Returns None.
        """

        self._item_fmt = value

        return None

    @property
    def auto_align(self) -> bool:
        """:class:`bool` Determines whether or not to align all of the prices
        (or items, depending which comes first in :attr:`item_fmt`) when
        generating entries.
        """

        return self._auto_align

    @auto_align.setter
    def auto_align(self, value: bool) -> None:

        self._auto_align = value

        return None

    def generate_report(self, output_file: str, **fmt) -> None:
        """Generates a new report and outputs to the path declared in
        :param:`output_file`.

        Parameters
        -----------
        output_file: :class:`str`
            The absolute or relative path to the desired output file.
        **fmt:
            Optional keyword arguments for users who use a custom template
            file. Use curly braces around dynamic attributes and define them
            here to use them in the final output.

        Returns None.
        """

        # Creates :attr:`entries` number of random items to add to report.
        entries: List[str] = [
            self.item_fmt.format(**self._random_item_and_price())
            for _ in range(self.entries)
        ]

        if (self.auto_align is True):
            entries = self._align_separator(entries)

        fmt['report'] = '\n'.join(entries)

        final_output: str = '\n'.join(self.template)

        if ('{name}' in final_output) and (fmt.get('name', None) is None):
            fmt['name'] = '_DefaultName'

        if ('{datetime}' in final_output) and (fmt.get('datetime', None) is None):
            fmt['datetime'] = datetime.now()

        with open(output_file, 'w+') as f:
            f.write(final_output.format(**fmt))

        return None

    def calculate_total(self, file_name: str) -> str:

        total: float = 0.00

        with open(file_name, 'r') as f:
            content: List[str] = f.readlines()

        separator: str = ' '.join(self._get_separators())

        for line in content:
            try:
                line, price = line.split(separator)

                if line.startswith('$'):
                    line, price = price, line

            except (IndexError, ValueError):
                continue

            total += float(price.strip().strip('$'))

        return f'${round(total, 2)}'

    def _cents(self) -> str:
        """[Internal Method]

        Returns a :class:`str` of an integer between 0 and 99.
        """

        cents: str = f'{randint(0, 99)}'

        return (cents
                if (len(cents) == 2)
                else f'0{cents}')

    def _price(self, key: str) -> str:
        """[Internal Method]

        Returns a :class:`str` of a price in dollar ('$0.00') format.
        """

        prices: dict = {
            '$': f'{randint(1, 4)}',
            '$$': f'{randint(5, 9)}',
            '$$$': f'{randint(10, 25)}'
        }

        dollar, cents = (prices[key], self._cents())

        return f'${dollar}.{cents}'

    def _random_item_and_price(self) -> dict:
        """[Internal Method]

        Returns a :class:`dict` with Keys: item, price.
        """

        _key: str = choice([k for k in self.inventory])

        return {
            'item': choice(self.inventory[_key]),
            'price': self._price(_key)
        }

    def _get_separators(self) -> List[str]:
        """[Internal Method]

        Returns a :class:`list` of all the words between '{item}'
        and '{price}', separated by a whitespace in :attr:`item_fmt`.
        """

        item_fmt_words = self.item_fmt.rsplit(maxsplit=2)

        words_to_search: List[str] = ['{item}', '{price}']

        for word in words_to_search:
            if (word not in item_fmt_words):
                error: str = ('Keywords %s and are required in the template.'
                              % (', '.join(words_to_search)))
                raise Exception(error)

        indexes: List[int] = sorted([item_fmt_words.index(word)
                                     for word in words_to_search])

        return (item_fmt_words[(indexes[0] + 1):indexes[1]])

    def _align_separator(self, _entries: List[str]) -> List[str]:
        """[Internal Method]

        Returns a :class:`list` of all the entries generated
        in :meth:`generate_report` with filler whitespaces to make all
        of the separators align in the output file.
        """

        separator: str = self._get_separators()[-1]

        result: List[str] = []

        entries = [entry.split(separator) for entry in _entries]
        items = [item for item, price in entries]

        for (index, (item, price)) in enumerate(entries):
            longest: int = len(max(items, key=len))
            current: int = len(items[index])

            spaces: str = (' ' * (longest - current))

            result.append(f'{item}{spaces}{separator}{price}')

        return result
