import { CompilerConfig } from '@ton/blueprint';

export const compile: CompilerConfig = {
    lang: 'tact',
    target: 'contracts/a_b_s_contract.tact',
    options: {
        debug: true,
    },
};
