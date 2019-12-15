//
// This code is placed into the PUBLIC DOMAIN.
// It was written by Douglas Burke dburke.gw@gmail.com
//
// Provide the Python interface to XSPEC local models using Sherpa.
//
// At present limited to:
//     zkerrbb.cxx (which calls zrunkbb.f)
//     agnslim.f
//

#include <iostream>

#include <xsTypes.h>

#include "sherpa/astro/xspec_extension.hh"

// We need a wrapper to convert from the C++ interface to the C-style
// interface (which is used by Sherpa). This code is taken from
// the XSPEC wrappers it generates for functions:
//  <heasoft>/Xspec/src/XSFunctions/funcWrappers.cxx
//
void cppModelWrapper(const double* energy, int nFlux, const double* params,
        int spectrumNumber, double* flux, double* fluxError, const char* initStr,
        int nPar, void (*cppFunc)(const RealArray&, const RealArray&,
        int, RealArray&, RealArray&, const string&))
{
   // Assumes energy points to arrays of size nFlux+1, flux and fluxError
   // point to arrays of size nFlux (though they need not be initialized),
   // and params points to an array of size nPar.
   RealArray energy_C(energy, (size_t)nFlux+1);
   RealArray params_C(params, nPar);
   RealArray flux_C(flux, (size_t)nFlux);
   RealArray fluxError_C(fluxError, (size_t)nFlux);
   string cppStr;
   if(initStr && strlen(initStr))
      cppStr = initStr;
   (*cppFunc)(energy_C, params_C, spectrumNumber, flux_C, fluxError_C, cppStr);
   for (int i=0; i<nFlux; ++i)
   {
      flux[i] = flux_C[i];
   }
   if (fluxError_C.size())
   {
      for (int i=0; i<nFlux; ++i)
      {
         fluxError[i] = fluxError_C[i];
      }
   }
}

extern "C" {

  void zkerrbb(const RealArray& energyArray, const RealArray& params,
	       int spectrumNumber, RealArray& flux, RealArray& fluxErr,
	       const string& initString);

  void C_zkerrbb(const double* energy, int nFlux, const double* params,
		 int spectrumNumber, double* flux, double* fluxError,
		 const char* initStr) {
    const size_t nPar = 9;

    cppModelWrapper(energy, nFlux, params, spectrumNumber, flux, fluxError,
		    initStr, nPar, zkerrbb);
  }

  void agnslim_(float* ear, int* ne, float* param, int* ifl, float* photar, float* photer);

  void thcompf_(float* ear, int* ne, float* param, int* ifl, float* photar, float* photer);

}


static PyMethodDef Wrappers[] = {
  // remember, the number of parameters here is 1 + <value from lmodel.dat>
  // for _NORM parameters.
  //
  XSPECMODELFCT_C_NORM( C_zkerrbb, 10 ),
  XSPECMODELFCT_NORM( agnslim, 15 ),
  XSPECMODELFCT_CON_F77( thcompf, 3 ),

  { NULL, NULL, 0, NULL }
};

static struct PyModuleDef wrapper_module = {
  PyModuleDef_HEAD_INIT,
  "_models",
  NULL,
  -1,
  Wrappers,
};

// Note that we are going to assume that the XSPEC model has
// already been initialized. The XSPECMODELFCT_C macro/template
// does not guarantee this (it does when building the Sherpa
// XSPEC module, but not for external code, since INIT_XSPEC
// may not be defined).
//
PyMODINIT_FUNC PyInit__models(void) {
  import_array();
  return PyModule_Create(&wrapper_module);
}
