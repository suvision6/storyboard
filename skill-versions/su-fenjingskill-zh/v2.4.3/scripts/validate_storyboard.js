#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const VERSION = "2.4.3";
const RULE_REVISION = "2.4.3-contract-integrity-p2-2026-07-12";

function usage() {
  console.error(
    "Usage (2.4.3): node validate_storyboard.js --python <python> " +
      "--data <shot_data.json> --markdown <storyboard.md> --excel <storyboard.xlsx> " +
      "--report <validation_report.json> --workspace-root <dir> [--final-signoff]"
  );
  console.error(
    "Usage (legacy validate): node validate_storyboard.js --python <python> " +
      "--data <shot_data.json> --markdown <storyboard.md> --excel <storyboard.xlsx> " +
      "[--report <validation_report.json>] [--workspace-root <dir>]"
  );
  console.error(
    `Wrapper ${VERSION} (${RULE_REVISION}): 2.4.3 validation requires both ` +
      "--report and --workspace-root; legacy validation keeps them optional."
  );
}

function parseArgs(argv) {
  const values = {};
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--final-signoff") {
      values.finalSignoff = true;
      continue;
    }
    if (!token.startsWith("--") || index + 1 >= argv.length) {
      throw new Error(`Invalid argument: ${token}`);
    }
    values[token.slice(2)] = argv[index + 1];
    index += 1;
  }
  return values;
}

let args;
try {
  args = parseArgs(process.argv.slice(2));
} catch (error) {
  usage();
  console.error(error.message);
  process.exit(2);
}

for (const key of ["data", "markdown", "excel"]) {
  if (!args[key]) {
    usage();
    console.error(`Missing --${key}`);
    process.exit(2);
  }
}

const python = args.python || process.env.CODEX_PYTHON || "python";
const validator = path.join(__dirname, "storyboard_delivery.py");
if (!fs.existsSync(validator)) {
  console.error(`Validator not found: ${validator}`);
  process.exit(2);
}

const child = spawnSync(
  python,
  [
    validator,
    "validate",
    "--data",
    args.data,
    "--markdown",
    args.markdown,
    "--excel",
    args.excel,
  ]
    .concat(args.report ? ["--report", args.report] : [])
    .concat(args["workspace-root"] ? ["--workspace-root", args["workspace-root"]] : [])
    .concat(args.finalSignoff ? ["--final-signoff"] : []),
  { stdio: "inherit", windowsHide: true }
);

if (child.error) {
  console.error(
    `Failed to start Python validator: ${child.error.message}. ` +
      "Pass the bundled Python executable with --python."
  );
  process.exit(2);
}
process.exit(child.status === null ? 2 : child.status);
