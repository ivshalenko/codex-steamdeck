import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import ts from 'typescript';

test('Decky callable names and argument counts match the Python plugin', () => {
  const main = fileURLToPath(new URL('../main.py', import.meta.url));
  const python = `
import ast,json,sys
from pathlib import Path
tree=ast.parse(Path(sys.argv[1]).read_text())
plugin=next(node for node in tree.body if isinstance(node,ast.ClassDef) and node.name=='Plugin')
methods={}
for node in plugin.body:
    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
        count=len(node.args.posonlyargs)+len(node.args.args)-1
        methods[node.name]={'min':count-len(node.args.defaults),'max':count}
print(json.dumps(methods))
`;
  const methods = JSON.parse(execFileSync('python3', ['-c', python, main], { encoding: 'utf8' }));
  const directory = new URL('../src/', import.meta.url);
  let checked = 0;
  for (const name of readdirSync(directory).filter(name => /\.tsx?$/.test(name))) {
    const source = ts.createSourceFile(name, readFileSync(new URL(name, directory), 'utf8'), ts.ScriptTarget.Latest, true);
    function visit(node) {
      if (ts.isCallExpression(node) && ts.isIdentifier(node.expression) && node.expression.text === 'callable') {
        const [parameters] = node.typeArguments || [];
        const [method] = node.arguments;
        assert.ok(parameters && ts.isTupleTypeNode(parameters), name);
        assert.ok(method && ts.isStringLiteral(method), name);
        const backend = methods[method.text];
        assert.ok(backend, `${name} calls an absent Python method ${method.text}`);
        const minimum = parameters.elements.filter(element =>
          !(ts.isNamedTupleMember(element) ? element.questionToken : ts.isOptionalTypeNode(element))).length;
        assert.ok(minimum >= backend.min, `${method.text} allows too few arguments`);
        assert.ok(parameters.elements.length <= backend.max, `${method.text} allows too many arguments`);
        checked++;
      }
      ts.forEachChild(node, visit);
    }
    visit(source);
  }
  assert.ok(checked > 0, 'No callable declarations were checked');
});
