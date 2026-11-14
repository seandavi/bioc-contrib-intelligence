import { expect, test } from "bun:test";
import { applyEdits, lineDiff } from "./draft";

test("applyEdits replaces exact unique text, all or nothing", () => {
  expect(applyEdits("a b c", [{ old_text: "b", new_text: "B" }, { old_text: "c", new_text: "C" }])).toEqual({ text: "a B C" });
  expect(applyEdits("a b b", [{ old_text: "b", new_text: "B" }])).toHaveProperty("error");
  expect(applyEdits("a b", [{ old_text: "b", new_text: "B" }, { old_text: "zz", new_text: "" }])).toHaveProperty("error");
  // a later edit sees the earlier one's result
  expect(applyEdits("x", [{ old_text: "x", new_text: "yy" }, { old_text: "yy", new_text: "z" }])).toEqual({ text: "z" });
});

test("lineDiff marks added and removed lines", () => {
  expect(lineDiff("a\nb\nc", "a\nB\nc")).toEqual([
    { op: " ", line: "a" }, { op: "-", line: "b" }, { op: "+", line: "B" }, { op: " ", line: "c" }]);
  expect(lineDiff("", "x").filter((d) => d.op !== " ")).toEqual([{ op: "-", line: "" }, { op: "+", line: "x" }]);
});
