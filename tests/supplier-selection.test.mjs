import test from 'node:test';
import assert from 'node:assert/strict';
import {comparisonIds} from '../lib/supplier-selection.mjs';
test('three matching selections exclude a previously saved supplier hidden by filters',()=>{
 assert.deepEqual(comparisonIds(['OLD','A','B','C'],[{supplierID:'A'},{supplierID:'B'},{supplierID:'C'},{supplierID:'D'}]),['A','B','C']);
});
test('matching suppliers that were not selected are never added',()=>{
 assert.deepEqual(comparisonIds(['B'],[{supplierID:'A'},{supplierID:'B'}]),['B']);
});
test('empty selection or no matching selections never loads example suppliers',()=>{
 assert.deepEqual(comparisonIds([],[{supplierID:'A'}]),[]);
 assert.deepEqual(comparisonIds(['A'],[]),[]);
});
test('selection spans result pages, with duplicates removed',()=>{
 const rows=Array.from({length:15},(_,i)=>({supplierID:String(i)}));
 assert.deepEqual(comparisonIds(['0','8','14','8'],rows),['0','8','14']);
});
