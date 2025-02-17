import { z } from 'zod';

function parseZodSubError (e: z.ZodIssueOptionalMessage, indent: number): string {
  if (e.code === z.ZodIssueCode.invalid_union) {
    return e.unionErrors
      .map(ue => parseZodErrorInternal(ue, indent + 2))
      .join("");
  }
  return "";
}

function parseZodErrorInternal (ze: z.ZodError, indent: number): string {
  return ze.errors
    .map(e => {
      return " ".repeat(indent) +
        "[" + e.path.join(", ") + "]" +
        ": " + e.message + "\n" +
        parseZodSubError(e, indent);
    })
    .join("\n");
}

export function parseZodError (ze: z.ZodError): string {
  return parseZodErrorInternal(ze, 10);
}
