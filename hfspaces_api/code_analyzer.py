"""Code analyzer for the gradio app code"""
import re
import ast

class SearchableAST:
    """Searchable AST for the gradio app code"""
    components = {
        "Textbox" : "string",
        "Number" : "number",
        "Slider" : "number",
        "Checkbox" : "string",
        "CheckboxGroup" : "list",
        "Radio" : "string",
        "Dropdown" : "string",
        "Image" : "data: image/jpeg;base64",
        "Video" : "data: video/mp4;base64",
        "Audio" : "data: data: video/mpeg;base64",
        "ColorPicker" : "String, Hexadecimal color code"
    }
    def __init__(self, raw_code):
        self.ast_tree = ast.parse(raw_code)

    def find_element(self, element_type: ast.AST, ast_tree: ast.AST = None):
        """Find the first element in AST Tree

        Args:
            element_type (ast.AST): object type to search
            ast_tree (ast.AST, optional): The ast object to start searching

        Returns:
            return_obj (ast.AST): If successful, returns object
        """        
        ast_tree = ast_tree or self.ast_tree
        return_obj = None
        for each in ast_tree.body:
            if isinstance(each, element_type):
                return_obj = each
            elif each.__dict__.get('body'):
                return_obj = self.find_element(element_type, each)
            if return_obj:
                break
        return return_obj

    def find_elements(self, element_type: type, ast_tree: ast.AST = None):
        """Find all elements in AST Tree

        Args:
            element_type (type): object type to search
            ast_tree (ast.AST, optional): The ast object to start searching

        Returns:
            element_bucket (List): Return all objects that matches, if no match return empty list.
        """
        ast_tree = ast_tree or self.ast_tree
        objs = []
        for each in ast_tree.body:
            if isinstance(each, element_type):
                objs.append(each)
            if each.__dict__.get('body'):
                objs.extend(self.find_elements(element_type, each))
        return objs

    def match_keyword(self, item: ast.AST, var_name: str):
        """Matches the keywords to given item

        Args:
            item (ast.AST): the item to be inspected
            var_name (str): the string to be matched

        Raises:
            NotImplementedError: raises when the AST object is not supported

        Returns:
            answer (ast.AST): Return AST object if there is match, otherwise None
        """        
        answer = None
        for name in item.targets:
            equality = False
            if isinstance(name, ast.Attribute):
                equality = re.search(var_name, name.attr)
            elif isinstance(name, ast.Name):
                equality = re.search(var_name, name.id)
            elif isinstance(name, ast.Tuple):
                equality = any(re.search(var_name, n.id) for n in name.elts)
            elif isinstance(name, ast.Subscript):
                continue
            else:
                raise NotImplementedError(ast.dump(name))

            if equality:
                answer = item
                break
        return answer

    def call_dispatcher(self, call_obj: ast.Call, attr_name: str):
        """Dispatch the items and make greedy search of call.

        Args:
            call_obj (ast.Call): The object to be decomposed
            attr_name (str): The attribute name to be matched

        Returns:
            bool : Return True if there is match, otherwise False
        """        
        return_obj = self._find_by_call_name(call_obj.func, attr_name)
        if return_obj:
            return True

        for each in call_obj.args:
            return_obj = self._find_by_call_name(each, attr_name)
            if return_obj:
                return True

        for each in call_obj.keywords:
            return_obj = self._find_by_call_name(each, attr_name)
            if return_obj:
                return True
        return False

    def _find_all_by_call_name(self, obj:ast.AST, attr_name: str):
        """Return a list of objects that match the call name

        Args:
            obj (ast.AST): The AST object to be inspected
            attr_name (str): The call name to be checked.

        Returns:
            objs (List): All calls that match the attr_name
        """
        objs = []
        if isinstance(obj, ast.Assign):
            objs.extend(self._find_all_by_call_name(obj.value, attr_name))
        elif isinstance(obj, ast.Expr):
            objs.extend(self._find_all_by_call_name(obj.value, attr_name))
        elif isinstance(obj, ast.Call):
            if self.call_dispatcher(obj, attr_name):
                objs.append(obj)
        elif isinstance(obj, ast.Name) and re.search(attr_name, obj.id):
            objs.append(obj)
        elif isinstance(obj, ast.Attribute) and re.search(attr_name, obj.attr):
            objs.append(obj)
        elif isinstance(obj, ast.Attribute):
            objs.extend(self._find_all_by_call_name(obj.value, attr_name))
        elif obj.__dict__.get('body') and not isinstance(obj.body, ast.Constant):
            for each in obj.body:
                return_obj = self._find_all_by_call_name(each, attr_name)
                objs.extend(return_obj)
        return objs

    def _find_by_call_name(self, obj: ast.AST, attr_name: str):
        """Return the first item that matches the call name

        Args:
            obj (ast.AST): The AST object to be inspected
            attr_name (str): The call name to be checked.

        Returns:
            return_obj (ast.AST): The first matching object, None if not found
        """
        return_obj = None
        if isinstance(obj, ast.Assign):
            return_obj = self._find_by_call_name(obj.value, attr_name)
        elif isinstance(obj, ast.Expr):
            return_obj = self._find_by_call_name(obj.value, attr_name)
        elif isinstance(obj, ast.Call):
            return_obj = self.call_dispatcher(obj, attr_name)
        elif isinstance(obj, ast.Name):
            if re.search(attr_name, obj.id):
                return_obj = obj
        elif isinstance(obj, ast.Attribute):
            if re.search(attr_name, obj.attr):
                return_obj = obj
            else:
                return_obj = self._find_by_call_name(obj.value, attr_name)
        elif obj.__dict__.get('body'):
            for each in obj.body:
                return_obj = self._find_by_call_name(each, attr_name)
                if return_obj:
                    break
        return return_obj

    def find_by_variable_name(self, var_name: str, ast_tree: ast.AST=None):
        """Finds item by variable name

        Args:
            var_name (str): _description_
            ast_tree (ast.AST, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        ast_tree = ast_tree or self.ast_tree
        return_obj = None
        for each in ast_tree.body:
            if isinstance(each, ast.Assign):
                return_obj = self.match_keyword(each, var_name)
            elif each.__dict__.get('body'):
                return_obj = self.find_by_variable_name(var_name, each)
            if return_obj:
                break
        return return_obj

    def find_by_attribute_name(self, attr_name: str, ast_tree: ast.AST = None):
        """_summary_

        Args:
            attr_name (str): _description_
            ast_tree (ast.AST, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        ast_tree = ast_tree or self.ast_tree
        return_obj = None
        for each in ast_tree.body:
            return_obj = self._find_all_by_call_name(each, attr_name)
            if return_obj:
                break
        return return_obj

    def find_all_by_attribute_name(self, attr_name: str, ast_tree: ast.AST = None):
        """_summary_

        Args:
            attr_name (str): _description_
            ast_tree (ast.AST, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        ast_tree = ast_tree or self.ast_tree
        objs = []
        for each in ast_tree.body:
            return_obj = self._find_all_by_call_name(each, attr_name)
            objs.extend(return_obj)
        return objs

    def get_keyword(self, call_obj: ast.Call, arg_name: str):
        """Get the value of a keyword of a call object

        Args:
            call_obj (ast.Call): _description_
            arg_name (str): _description_

        Returns:
            _type_: _description_
        """
        for k in call_obj.keywords:
            if k.arg == arg_name:
                return k.value
        return None

    def get_item_value(self, item: ast.AST, component_search=False):
        """Return the item name respective to item type

        Args:
            item (ast.AST): _description_

        Returns:
            _type_: _description_
        """
        return_obj = ""
        if isinstance(item, ast.Name):
            line = self.find_by_variable_name(item.id)
            return_obj = self.get_item_value(line.value, component_search)
        elif isinstance(item, ast.Constant):
            return_obj = item.value
        elif isinstance(item, ast.Attribute):
            if isinstance(item.value, (ast.Call)):
                return_obj = self.get_item_value(item.value)
            else:
                return_obj = item.attr
        elif isinstance(item, ast.Assign):
            return_obj = self.get_item_value(item.targets[0], component_search)
        elif isinstance(item, ast.Subscript):
            origin_obj = self.find_by_variable_name(item.value.id)
            return_obj = self.get_item_value(origin_obj)
        elif isinstance(item, ast.Call):
            if isinstance(item.func, ast.Name):
                return_obj = item.func.id
            return_obj = self.get_item_value(item.func, component_search)
        elif isinstance(item, ast.List):
            return_obj = [self.get_item_value(
                i, component_search) for i in item.elts]
            if component_search:
                return_obj = [i if i in self.components else "Unknown" for i in return_obj]
            return return_obj
        else:
            return_obj = item

        if component_search:
            return_obj = return_obj if return_obj in self.components else "Unknown"
        return return_obj

    def summarize_var(self, line_call: ast.Name):
        """Summarize a list

        Args:
            line_call (ast.Name): _description_

        Returns:
            _type_: _description_
        """
        output = {}
        output["type"] = self.get_item_value(line_call, True)
        if output["type"] in ('Dropdown', 'CheckboxGroup', 'Radio'):
            output["choice"] = self.get_keyword(line_call, 'choices')
        output["default"] = self.get_keyword(line_call, 'default')
        output["value"] = self.get_keyword(line_call, 'value')
        output["label"] = self.get_keyword(line_call, 'label')
        output["placeholder"] = self.get_keyword(line_call, 'placeholder')
        output["visible"] = self.get_keyword(line_call, 'visible')
        output = {k: self.get_item_value(v) for k, v in output.items() if v is not None}
        output["expected datatype"] = self.components.get(output["type"], "Unknown type")
        return output

    def unravel_list(self, list_obj: ast.List):
        """Given a list object, find the items and return schema form

        Args:
            list_obj (ast.List): the list obj to unravel

        Raises:
            TypeError: If the given description is not expected inside the list, a TypeError raises

        Returns:
            out_dictionary (dict): a summary of the function.
        """
        out_dictionary = []
        for param in list_obj.elts:
            if isinstance(param, ast.Name):
                line_call = self.find_by_variable_name(param.id).value
                out_dictionary += [self.summarize_var(line_call)]
            elif isinstance(param, ast.Constant):
                out_dictionary += [{'type' : param.value}]
            elif isinstance(param, ast.Call):
                out_dictionary += [self.summarize_var(param)]
            else:
                raise TypeError(f"{type(param)}  is not expected inside the list")
        return out_dictionary

    def get_schema(self, click_obj: ast.Call):
        """Return the schema for click

        Args:
            click_obj (ast.Call): _description_

        Returns:
            _type_: _description_
        """
        input_items = self.get_keyword(click_obj, 'inputs')

        if isinstance(input_items, ast.Name):
            input_items = self.find_by_variable_name(input_items.id).value
        if isinstance(input_items, ast.Call):
            input_items = [self.summarize_var(input_items)]
        if isinstance(input_items, ast.List):
            input_items = self.unravel_list(input_items)
        if isinstance(input_items, ast.Constant):
            input_items = [{"type": input_items.value}]

        return input_items
